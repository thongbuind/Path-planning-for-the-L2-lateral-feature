"""ASAM XML adapter for the supported single-ego benchmark subset.

OpenSCENARIO 1.3.1; OpenDRIVE 1.8.1. This is deliberately not a general
OpenSCENARIO interpreter. Simulator-specific behavior uses pp:* extensions.
"""
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import numpy as np

from eval import departure
from interfaces import LineType, RoadEdgeType
from sim.faults.channel import ChannelFault
from sim.faults.ego_motion import EgoMotionFault
from sim.faults.lane import LaneFault
from sim.faults.sensor import SensorFault
from sim.runtime.clock import ClockFault
from sim.scenario import Scenario
from sim.vehicle.profiles import PROFILES
from sim.world.road import Marking, RoadEdgeSpec, RoadLayout, Segment
from sim.world.traffic import LateralMotion, TrafficSpec

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'benchmark' / 'schema'
TOKEN = re.compile(r'\$([A-Za-z_][A-Za-z0-9_]*)')
# Largest camera view the planner uses: curvature buffer 0-126 m (Interface Control Document 5.1).
CAMERA_VIEW_MAX_M = 126.0


def number(value):
    v = float(value)
    if not math.isfinite(v):
        raise ValueError(f'non-finite number: {value}')
    return v


def text(value):
    if isinstance(value, bool):
        return str(value).lower()
    return repr(value) if isinstance(value, float) else str(value)


def node(parent, tag, **attrs):
    return ET.SubElement(parent, tag, {k: text(v) for k, v in attrs.items()})


def document(description):
    root = ET.Element('OpenSCENARIO')
    node(root, 'FileHeader', author='Path Planner', date='2026-11-11T00:00:00Z',
         description=description, revMajor=1, revMinor=3)
    return root


def write(root, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space='  ')
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)


def parse(path):
    data = Path(path).read_bytes()
    if b'<!DOCTYPE' in data or b'<!ENTITY' in data:
        raise ValueError('DTD and entity declarations are not supported')
    return ET.fromstring(data)


def declarations(root):
    result = {}
    for p in root.findall('./ParameterDeclarations/ParameterDeclaration'):
        name, value = p.attrib['name'], p.attrib['value']
        if name in result:
            raise ValueError(f'duplicate parameter {name}')
        if p.attrib['parameterType'] == 'double':
            value = number(value)
        elif p.attrib['parameterType'] == 'boolean':
            if value not in ('true', 'false'):
                raise ValueError(f'invalid boolean {value}')
            value = value == 'true'
        elif p.attrib['parameterType'] != 'string':
            raise ValueError(f'unsupported parameter type: {p.attrib}')
        result[name] = value
    return result


def resolve(root, overrides=None):
    root = deepcopy(root)
    params = declarations(root)
    unknown = set(overrides or {}) - params.keys()
    if unknown:
        raise ValueError(f'undeclared parameters: {sorted(unknown)}')
    params.update(overrides or {})
    # Validate overrides through the same typed declarations.
    for p in root.findall('./ParameterDeclarations/ParameterDeclaration'):
        p.set('value', text(params[p.attrib['name']]))
    params = declarations(root)
    def sub(value):
        return TOKEN.sub(lambda m: text(params[m[1]]), value)
    for element in root.iter():
        for key, value in list(element.attrib.items()):
            element.set(key, sub(value))
        if element.text and '$' in element.text:
            element.text = sub(element.text)
    return root, params


def parameter_sets(path, suffix):
    """Named, coupled assignments. IDs never depend on list position."""
    root = parse(Path(path).with_suffix(suffix))
    reference = root.find('./ParameterValueDistribution/ScenarioFile')
    if reference is None or reference.get('filepath') != Path(path).name:
        raise ValueError('parameter distribution references the wrong scenario')
    result = {}
    for values in root.findall('.//ParameterValueSet'):
        params = {p.attrib['parameterRef']: p.attrib['value'] for p in values}
        key = params['variant']
        if key in result:
            raise ValueError(f'duplicate parameter set {key}')
        result[key] = params
    return result


def anchors(path):
    return parameter_sets(path, '.anchors.xosc')


@lru_cache(maxsize=4096)
def geometry_end(x, y, heading, length, k0, k1):
    """Analytic heading, Gauss-Legendre integration of the spiral's position."""
    z, weights = np.polynomial.legendre.leggauss(32)
    u = (z + 1) * length / 2
    angle = heading + k0 * u + (k1 - k0) * u * u / (2 * length)
    return (x + length / 2 * float(weights @ np.cos(angle)),
            y + length / 2 * float(weights @ np.sin(angle)),
            heading + (k0 + k1) * length / 2)


def road_xml(segments, lane_width):
    root = ET.Element('OpenDRIVE')
    node(root, 'header', revMajor=1, revMinor=8, name='ego lane reference', version='1.0')
    road = node(root, 'road', name='three lanes', length=sum(s.length for s in segments),
                id='1', junction='-1', rule='RHT')
    plan = node(road, 'planView')
    x = y = heading = distance = previous = 0.0
    for seg in segments:
        g = node(plan, 'geometry', s=distance, x=x, y=y, hdg=heading, length=seg.length)
        k0 = previous if seg.kind == 'clothoid' else seg.curvature_end
        k1 = seg.curvature_end
        if seg.kind == 'straight':
            node(g, 'line')
            k0 = k1 = 0.0
        elif seg.kind == 'arc':
            if abs(k1) < 1e-15:
                node(g, 'line')
            else:
                node(g, 'arc', curvature=k1)
        else:
            node(g, 'spiral', curvStart=k0, curvEnd=k1)
        x, y, heading = geometry_end(x, y, heading, seg.length, k0, k1)
        distance += seg.length
        previous = k1
    lanes = node(road, 'lanes')
    # Reference line is the centre of lane -2, preserving the simulator's Frenet frame.
    node(lanes, 'laneOffset', s=0, a=1.5 * lane_width, b=0, c=0, d=0)
    section = node(lanes, 'laneSection', s=0)
    centre = node(node(section, 'center'), 'lane', id=0, type='none', level=False)
    node(centre, 'roadMark', sOffset=0, type='solid', weight='standard', color='white', width=.15)
    right = node(section, 'right')
    for i in (1, 2, 3):
        lane = node(right, 'lane', id=-i, type='driving', level=False)
        node(lane, 'width', sOffset=0, a=lane_width, b=0, c=0, d=0)
        node(lane, 'roadMark', sOffset=0, type='solid' if i == 3 else 'broken',
             weight='standard', color='white', width=.15)
    return root


def _road_signature(element):
    def value(v):
        try:
            return number(v)
        except ValueError:
            return v
    return (element.tag, sorted((key, value(v)) for key, v in element.attrib.items()),
            [_road_signature(child) for child in element])


def _road_cross_section(road):
    lanes = road.find('lanes')
    if lanes is None or len(lanes.findall('laneSection')) != 1 or len(lanes.findall('laneOffset')) != 1:
        raise ValueError('one lane section and offset required')
    section = lanes.find('laneSection')
    rights = section.findall('./right/lane')
    centre = section.findall('./center/lane')
    if (number(section.attrib['s']) != 0 or not 1 <= len(rights) <= 3
            or [lane.get('id') for lane in rights] != [str(-i - 1) for i in range(len(rights))]
            or len(centre) != 1 or centre[0].get('id') != '0' or centre[0].get('type') != 'none'):
        raise ValueError('expected one to three right driving lanes starting at zero')
    widths = []
    for lane in rights:
        if lane.get('type') != 'driving' or len(lane.findall('width')) != 1:
            raise ValueError('one constant width per driving lane required')
        w = lane.find('width')
        if any(number(w.attrib[k]) != 0 for k in ('sOffset', 'b', 'c', 'd')):
            raise ValueError('variable lane width unsupported')
        widths.append(number(w.attrib['a']))
    offset = lanes.find('laneOffset')
    if len(set(widths)) != 1 or widths[0] <= 0 or any(number(offset.attrib[k]) != 0 for k in ('s', 'b', 'c', 'd')):
        raise ValueError('unequal lane widths or variable lane offset unsupported')
    width = widths[0]
    lane_position = number(offset.attrib['a']) / width - 0.5
    ego = round(lane_position)
    if not 0 <= ego < len(rights) or not math.isclose(lane_position, ego, abs_tol=1e-9):
        raise ValueError('the ego lane must be centred on the reference line')
    return width, ego, centre + rights


_EDGE_MARKS = {'edge': RoadEdgeType.UNKNOWN, 'grass': RoadEdgeType.GRASS_GRAVEL,
               'curb': RoadEdgeType.CURB}
_DOUBLE_MARKS = {'solid solid', 'broken solid', 'solid broken', 'broken broken'}


def _barrier_geometry(obj, road_length):
    repeat = obj.findall('repeat')
    if (obj.get('type') != 'barrier' or obj.get('dynamic', 'no') != 'no'
            or any(number(obj.get(name, 0)) != 0 for name in ('s', 'hdg', 'pitch', 'roll'))
            or len(repeat) != 1 or repeat[0].get('detachFromReferenceLine', 'false') != 'false'):
        raise ValueError('only static barriers following the full road are supported')
    span = repeat[0]
    t, width = number(span.attrib['tStart']), number(span.get('widthStart', obj.get('width', 0)))
    if (number(span.attrib['s']) != 0 or number(span.attrib['distance']) != 0
            or not math.isclose(number(span.attrib['length']), road_length, abs_tol=1e-7)
            or number(span.attrib['tEnd']) != t or number(span.get('widthEnd', obj.get('width', 0))) != width
            or width <= 0 or abs(t) <= width / 2):
        raise ValueError('a barrier must have a constant offset and width along the full road')
    return t, width, span


def _layout_from_road(road, segments, width, ego, lanes):
    expected = road_xml(segments, width).find('road/lanes')
    if road.find('objects') is None and _road_signature(road.find('lanes')) == _road_signature(expected):
        return None  # preserve the original HWA boundary offsets

    markings = {}
    edges = [None, None]
    for index, lane in enumerate(lanes):
        marks = lane.findall('roadMark')
        if not marks:
            continue
        if len(marks) != 1 or number(marks[0].attrib['sOffset']) != 0:
            raise ValueError('only one constant marking per boundary is supported')
        mark = marks[0]
        kind = mark.attrib['type']
        offset = (ego + 0.5 - index) * width
        if kind == 'none':
            continue
        if kind in _EDGE_MARKS:
            if index not in (0, len(lanes) - 1):
                raise ValueError('physical road edge must delimit the road')
            edges[0 if offset > 0 else 1] = RoadEdgeSpec(offset, _EDGE_MARKS[kind])
            continue
        if kind not in {'solid', 'broken'} | _DOUBLE_MARKS:
            raise ValueError(f'unsupported road marking: {kind}')
        paint_width = number(mark.attrib['width'])
        if not 0 < paint_width < width:
            raise ValueError('invalid marking width')
        near_side = kind.split()[-1 if index <= ego else 0]
        line_type = LineType.DOUBLE if kind in _DOUBLE_MARKS else (
            LineType.DASHED if kind == 'broken' else LineType.SOLID)
        markings[index] = Marking(offset - math.copysign(paint_width / 2, offset), line_type,
                                  near_side == 'broken')
    for obj in road.findall('./objects/object'):
        t, thickness, _ = _barrier_geometry(obj, number(road.attrib['length']))
        side = 0 if t > 0 else 1
        face = t - math.copysign(thickness / 2, t)
        if edges[side] is None or abs(face) <= abs(edges[side].offset_m):
            edges[side] = RoadEdgeSpec(face, RoadEdgeType.BARRIER)
    return RoadLayout(tuple(markings.get(index) for index in range(ego - 1, ego + 3)), tuple(edges))


def _set_road_width(road, new_width):
    width, ego, lanes = _road_cross_section(road)
    if new_width == width:
        return
    offset = road.find('./lanes/laneOffset')
    offset.set('a', text((ego + 0.5) * new_width))
    for lane in lanes[1:]:
        lane.find('width').set('a', text(new_width))
    for obj in road.findall('./objects/object'):
        t, thickness, span = _barrier_geometry(obj, number(road.attrib['length']))
        half = math.copysign(thickness / 2, t)
        scaled_t = (t - half) * new_width / width + half
        obj.set('t', text(scaled_t))
        span.set('tStart', text(scaled_t))
        span.set('tEnd', text(scaled_t))


def _read_road(root, width_override=None):
    allowed = {'OpenDRIVE', 'header', 'road', 'planView', 'geometry', 'line', 'arc',
               'spiral', 'lanes', 'laneOffset', 'laneSection', 'center', 'right',
               'lane', 'width', 'roadMark', 'objects', 'object', 'repeat'}
    if root.tag != 'OpenDRIVE' or any(e.tag not in allowed for e in root.iter()) or len(root.findall('road')) != 1:
        raise ValueError('unsupported OpenDRIVE subset: one flat road with constant-width lanes required')
    road = root.find('road')
    if road is None or road.get('id') != '1' or road.get('junction') != '-1' or road.get('rule') != 'RHT':
        raise ValueError('expected non-junction road 1')
    segments = []
    x = y = heading = distance = previous = 0.0
    for g in road.findall('./planView/geometry'):
        if len(g) != 1:
            raise ValueError('one geometry primitive required')
        for key, expected in [('s', distance), ('x', x), ('y', y), ('hdg', heading)]:
            if not math.isclose(number(g.attrib[key]), expected, abs_tol=1e-7):
                raise ValueError(f'discontinuous road geometry: {key}')
        length = number(g.attrib['length'])
        shape = g[0]
        k1 = 0.0 if shape.tag == 'line' else number(shape.attrib['curvature' if shape.tag == 'arc' else 'curvEnd'])
        k0 = previous if shape.tag == 'spiral' else k1
        if shape.tag == 'spiral' and not math.isclose(number(shape.attrib['curvStart']), k0, abs_tol=1e-12):
            raise ValueError('discontinuous spiral curvature')
        segments.append(Segment({'line': 'straight', 'arc': 'arc', 'spiral': 'clothoid'}[shape.tag], length, k1))
        x, y, heading = geometry_end(x, y, heading, length, k0, k1)
        distance += length
        previous = k1
    if not segments or not math.isclose(number(road.attrib['length']), distance, abs_tol=1e-7):
        raise ValueError('road length mismatch')
    if width_override is not None:
        _set_road_width(road, width_override)
    width, ego, lanes = _road_cross_section(road)
    layout = _layout_from_road(road, segments, width, ego, lanes)
    return tuple(segments), width, layout


def read_road(path):
    segments, width, _ = _read_road(parse(path))
    return segments, width


# Fault commands beyond the lane model (Software Qualification Test Specification 6): command
# type -> (Scenario field, fault class). JSON fields are those of the class; duration -1 is
# until the end of the run.
FAULT_COMMANDS = {
    'pp:channel_fault:v1': ('channel_faults', ChannelFault),
    'pp:sensor_fault:v1': ('sensor_faults', SensorFault),
    'pp:clock_fault:v1': ('clock_faults', ClockFault),
    'pp:ego_motion_fault:v1': ('ego_motion_faults', EgoMotionFault),
}


def request_events(spec):
    """{"events": [{"at_s": t, "requests": [[state, side, elk_reason], x3], "driver_override": bool}]}
    -> RequestEvent tuple; names of the Interface Control Document 5.6 enums, tlc infinite."""
    from interfaces import CancelReason, ElkReason, FunctionRequest, RequestState, Side
    from sim.stand_ins.scripted import RequestEvent
    events = []
    for event in spec.get('events', []):
        if set(event) - {'at_s', 'requests', 'driver_override'} or len(event['requests']) != 3:
            raise ValueError('a request event needs at_s and three requests')
        requests = tuple(FunctionRequest(RequestState[state], Side[side], math.inf, ElkReason[reason],
                                         CancelReason.NONE) for state, side, reason in event['requests'])
        events.append(RequestEvent(round(number(event['at_s']) * 1e6), requests,
                                   bool(event.get('driver_override', False))))
    return tuple(events)


# Simulator values a scenario may set (Software Qualification Test Specification 4.4 to 4.6, 6.2):
# property pp:<field> -> Scenario field. Within eval.sweep.check_sim.
SIM_PROPERTIES_FIELDS = ('road_mu', 'eps_delay_s', 'perception_noise_scale', 'camera_latency_ms')
SIM_PROPERTIES = tuple('pp:' + f for f in SIM_PROPERTIES_FIELDS)


def fault_of_command(command):
    """(Scenario field, fault) of one fault command of any type."""
    kind = command.get('type')
    if kind == 'pp:lane_fault:v1':
        return 'lane_faults', fault_from_command(command)
    if kind not in FAULT_COMMANDS:
        raise ValueError(f'unsupported custom command {kind}')
    field_name, cls = FAULT_COMMANDS[kind]
    spec = json.loads(command.text or '{}')
    if 'trigger' in spec and cls is ClockFault:
        raise ValueError('clock faults hold for the whole run; they take no trigger')
    if spec.get('duration_s') == -1:
        spec['duration_s'] = None
    if 'indices' in spec:
        spec['indices'] = tuple(spec['indices'])
    for key in ('every', 'count'):
        if key in spec:
            if spec[key] != int(spec[key]):
                raise ValueError(f'{key} must be a whole number')
            spec[key] = int(spec[key])
    for key, value in spec.items():
        if isinstance(value, float):
            number(value)
    return field_name, cls(**spec)


def fault_from_command(command):
    if command.get('type') != 'pp:lane_fault:v1':
        raise ValueError(f'unsupported custom command {command.get("type")}')
    spec = json.loads(command.text or '{}')
    if 'value_between' in spec:
        # A value between two calibration limits of the build under test (F21 e:
        # confidence between conf_ego and conf_inferred), as a bench reads the A2L.
        from eval.calibration import requirement_parameters
        cal = requirement_parameters()
        low, high = (cal[name] for name in spec.pop('value_between'))
        spec['value'] = 0.5 * (low + high)
    if 'edges' in spec:
        spec['edges'] = tuple(spec['edges'])
    if spec.get('duration_s') == -1:
        spec['duration_s'] = None
    spec['lines'] = tuple(spec['lines'])
    fault = LaneFault(**spec)
    if (fault.start_s < 0 or (fault.duration_s is not None and fault.duration_s <= 0)
            or not fault.lines or any(i not in (0, 1, 2, 3) for i in fault.lines)
            or fault.sigma_c0 < 0 or fault.sigma_c1 < 0
            or (fault.kind == 'fade_line' and fault.value <= 0)
            or (fault.kind.startswith('view_') and not fault.value > 0)
            or any(i not in (0, 1) for i in fault.edges)):
        raise ValueError('invalid lane fault parameters')
    for v in (fault.start_s, fault.value, fault.sigma_c0, fault.sigma_c1):
        number(v)
    if fault.duration_s is not None:
        number(fault.duration_s)
    return fault


def load_scenario(path, overrides=None):
    path = Path(path)
    root, params = resolve(parse(path), overrides)
    if root.tag != 'OpenSCENARIO' or root.find('Storyboard') is None:
        raise ValueError('expected OpenSCENARIO scenario document')
    supported = {'OpenSCENARIO', 'FileHeader', 'License', 'Properties', 'Property',
                 'ParameterDeclarations', 'ParameterDeclaration', 'CatalogLocations',
                 'RoadNetwork', 'LogicFile', 'Entities', 'ScenarioObject', 'Vehicle',
                 'BoundingBox', 'Center', 'Dimensions', 'Performance', 'Axles',
                 'FrontAxle', 'RearAxle', 'Storyboard', 'Init', 'Actions',
                 'UserDefinedAction', 'CustomCommandAction', 'Private', 'PrivateAction',
                 'TeleportAction', 'Position', 'RoadPosition', 'Orientation',
                 'LongitudinalAction', 'SpeedAction', 'SpeedActionDynamics',
                 'SpeedActionTarget', 'AbsoluteTargetSpeed', 'StopTrigger',
                 'ConditionGroup', 'Condition', 'ByValueCondition', 'SimulationTimeCondition'}
    unsupported = {e.tag for e in root.iter()} - supported
    if unsupported:
        raise ValueError(f'unsupported OpenSCENARIO elements: {sorted(unsupported)}')
    # Unsupported dynamic content must never be silently ignored.
    if root.findall('.//Story') or root.findall('.//GlobalAction') or root.findall('.//CatalogReference'):
        raise ValueError('stories, global actions and catalog references are unsupported')
    objects = root.findall('./Entities/ScenarioObject')
    if not objects or objects[0].get('name') != 'Ego' or len({o.get('name') for o in objects}) != len(objects):
        raise ValueError('Ego must be the first entity; entity names must be unique')
    properties = {p.get('name'): p.get('value') for p in objects[0].findall('./Vehicle/Properties/Property')}
    required = {'pp:adapter', 'pp:profile', 'pp:acc', 'pp:hwa_request_s', 'pp:hold_until_hwa'}
    optional = {'pp:camera_view_m', 'pp:camera_view_start_m', 'pp:adas_mode', 'pp:lka_enabled', 'pp:elk_enabled',
                'pp:expect_intervention', 'pp:protocol', 'pp:hwa_view_gate', 'pp:expected_outcome',
                'pp:can_bus', 'pp:realism', 'pp:loop', 'pp:faults'} | set(SIM_PROPERTIES)
    if not required <= set(properties) <= required | optional:
        raise ValueError('unsupported or missing simulator properties')
    if properties.get('pp:adapter') != 'single-ego-v1':
        raise ValueError('missing pp:adapter single-ego-v1')
    if properties['pp:profile'] not in PROFILES or properties['pp:acc'] not in ('off', 'on', 'ignore_limits'):
        raise ValueError('unknown profile or ACC mode')
    privates = {p.get('entityRef'): p for p in root.findall('./Storyboard/Init/Actions/Private')}
    if set(privates) != {o.get('name') for o in objects}:
        raise ValueError('every entity needs exactly one Private with its initial actions')
    def initial(name):
        actions = privates[name].findall('PrivateAction')
        if len(actions) != 2 or actions[0].find('TeleportAction') is None or actions[1].find('LongitudinalAction/SpeedAction') is None:
            raise ValueError('only initial teleport and absolute speed are supported')
        pos = actions[0].find('TeleportAction/Position/RoadPosition')
        spd = actions[1].find('LongitudinalAction/SpeedAction/SpeedActionTarget/AbsoluteTargetSpeed')
        dyn = actions[1].find('LongitudinalAction/SpeedAction/SpeedActionDynamics')
        if pos is None or spd is None or pos.get('roadId') != '1':
            raise ValueError('road position and absolute speed required')
        if dyn is None or dyn.get('dynamicsShape') != 'step' or dyn.get('dynamicsDimension') != 'time' or number(dyn.get('value')) != 0:
            raise ValueError('only instantaneous initial speed supported')
        return pos, spd
    position, speed = initial('Ego')
    traffic = []
    for i, obj in enumerate(objects[1:], start=1):
        pos, spd = initial(obj.get('name'))
        dims = obj.find('./Vehicle/BoundingBox/Dimensions')
        if obj.find('./Vehicle/Properties') is not None or dims is None:
            raise ValueError('traffic vehicles need a bounding box and no simulator properties')
        heading = pos.find('Orientation')
        travel_direction = 1
        if heading is not None:
            angle = abs(math.remainder(number(heading.get('h', 0)), 2 * math.pi))
            if (heading.get('type') != 'relative' or any(number(heading.get(axis, 0)) != 0 for axis in ('p', 'r'))
                    or not (angle == 0 or math.isclose(angle, math.pi, abs_tol=1e-9))):
                raise ValueError('traffic heading must be relative to the road, 0 or pi')
            travel_direction = 1 if angle == 0 else -1
        traffic.append(TrafficSpec(i, number(pos.get('s')), number(pos.get('t')), number(spd.get('value')),
                                   number(dims.get('length')), number(dims.get('width')), travel_direction))
    stop = root.find('./Storyboard/StopTrigger/ConditionGroup/Condition/ByValueCondition/SimulationTimeCondition')
    if stop is None:
        raise ValueError('time stop required')
    groups = root.findall('./Storyboard/StopTrigger/ConditionGroup')
    conditions = root.findall('./Storyboard/StopTrigger/ConditionGroup/Condition')
    if len(groups) != 1 or len(conditions) != 1 or conditions[0].get('conditionEdge') != 'none' or number(conditions[0].get('delay')) != 0:
        raise ValueError('only one immediate simulation time stop supported')
    if stop.get('rule') != 'greaterOrEqual':
        raise ValueError('only greaterOrEqual time stop supported')
    road_file = root.find('./RoadNetwork/LogicFile')
    width_override = number(params['lane_width_m']) if 'lane_width_m' in params else None
    segments, width, layout = _read_road(parse(path.parent / road_file.attrib['filepath']), width_override)
    scale = number(params.get('curvature_scale', 1))
    direction = number(params.get('direction', 1))
    if scale <= 0 or direction not in (-1, 1):
        raise ValueError('positive curvature_scale and direction +/-1 required')
    segments = tuple(Segment(s.kind, s.length, s.curvature_end * scale * direction) for s in segments)
    faults, departure_specs, extra_faults, request_specs = [], [], {}, []
    names = [o.get('name') for o in objects[1:]]
    for command in root.findall('./Storyboard/Init/Actions/UserDefinedAction/CustomCommandAction'):
        if command.get('type') == 'pp:departure:v1':
            departure_specs.append(json.loads(command.text or '{}'))
        elif command.get('type') == 'pp:traffic_speed:v1':
            # Speed of another vehicle over time (S11), as an ASAM story would set it.
            spec = json.loads(command.text or '{}')
            if set(spec) != {'entity', 'profile'} or spec['entity'] not in names:
                raise ValueError('pp:traffic_speed:v1 needs a known entity and a profile')
            i = names.index(spec['entity'])
            profile = tuple((number(t), number(v)) for t, v in spec['profile'])
            traffic[i] = replace(traffic[i], speed_profile=profile)
        elif command.get('type') == 'pp:traffic_lateral:v1':
            # Lane change or cut-in of another vehicle (S3b, S11 d): sim.world.traffic.LateralMotion.
            spec = json.loads(command.text or '{}')
            if set(spec) != {'entity', 'start_s', 'duration_s', 'target_offset_m'} or spec['entity'] not in names:
                raise ValueError('pp:traffic_lateral:v1 needs entity, start_s, duration_s, target_offset_m')
            i = names.index(spec.pop('entity'))
            traffic[i] = replace(traffic[i], lateral_motion=LateralMotion(**{k: number(v) for k, v in spec.items()}))
        elif command.get('type') == 'pp:requests:v1':
            # Scripted FunctionRequests (S9, S16): frames HWA, LKA, ELK from each time on.
            request_specs.append(json.loads(command.text or '{}'))
        else:
            field_name, fault = fault_of_command(command)
            extra_faults.setdefault(field_name, []).append(fault)
    if len(departure_specs) > 1:
        raise ValueError('only one departure setup is supported')
    orientation = position.find('Orientation')
    if orientation is None or orientation.get('type') != 'relative' or any(number(orientation.get(k, 0)) != 0 for k in ('p', 'r')):
        raise ValueError('relative road orientation required')
    def flag(key):
        value = properties.get('pp:' + key, 'false')
        if value not in ('true', 'false'):
            raise ValueError(f'invalid {key}')
        return value == 'true'

    hwa = properties['pp:hwa_request_s']
    expect = properties.get('pp:expect_intervention', '')
    protocol = properties.get('pp:protocol', '')
    if expect not in ('', 'LKA', 'ELK', 'late ELK') or protocol not in ('', 'Euro NCAP LSS', 'EU 2021/646'):
        raise ValueError('unknown intervention expectation or protocol')
    outcome = properties.get('pp:expected_outcome', '')
    if outcome not in ('', 'drive', 'drive_limited', 'refuse'):
        raise ValueError('unknown expected outcome (Software Qualification Test Specification 5.3)')
    notes = {'description': params.get('description', '')}
    if outcome:
        notes['expected_outcome'] = outcome
    if properties.get('pp:faults'):
        notes['faults'] = properties['pp:faults'].split(',')
    if expect:
        notes['expect_intervention'] = expect
    if protocol:
        notes['protocol'] = protocol
    scenario = Scenario(
        name=params['scenario_id'] + params['variant'], segments=segments, lane_width=width,
        speed_mps=number(speed.attrib['value']), profile=properties['pp:profile'],
        duration_s=number(stop.attrib['value']), hwa_request_s=None if hwa == 'off' else number(hwa),
        start_s=number(position.attrib['s']), start_offset_m=number(position.attrib['t']),
        start_heading_rad=number(orientation.attrib['h']), hold_until_hwa=flag('hold_until_hwa'),
        acc=properties['pp:acc'], lane_faults=tuple(extra_faults.pop('lane_faults', [])),
        **{name: tuple(items) for name, items in extra_faults.items()},
        can_bus=flag('can_bus'), realism=flag('realism'), loop=properties.get('pp:loop', 'closed') or 'closed',
        camera_view_m=number(properties.get('pp:camera_view_m', 80.0)),
        camera_view_start_m=number(properties.get('pp:camera_view_start_m', 0.0)),
        traffic=tuple(traffic),
        notes=notes, road_layout=layout, adas_mode=properties.get('pp:adas_mode', 'scripted'),
        lka_enabled=flag('lka_enabled'), elk_enabled=flag('elk_enabled'),
        hwa_view_gate=flag('hwa_view_gate'),
        **{field: number(properties['pp:' + field]) for field in SIM_PROPERTIES_FIELDS if 'pp:' + field in properties})
    if request_specs:
        if len(request_specs) > 1 or scenario.adas_mode != 'scripted':
            raise ValueError('one pp:requests:v1, in scripted ADAS mode')
        scenario = replace(scenario, request_events=request_events(request_specs[0]))
    if departure_specs:
        scenario = departure.configure(scenario, **departure_specs[0])
    from eval.sweep import check_sim
    check_sim(scenario)
    if not 2.5 <= width <= 5.5 or not 0 <= scenario.speed_mps <= 130 / 3.6 + 1e-10:
        raise ValueError('lane width or speed outside benchmark ODD')
    if not (10.0 <= scenario.camera_view_m <= CAMERA_VIEW_MAX_M
            and 0.0 <= scenario.camera_view_start_m < scenario.camera_view_m):
        raise ValueError('camera view outside 0 <= start < end, 10 <= end <= 126 m')
    if (scenario.duration_s <= 0 or (scenario.hwa_request_s is None and scenario.hold_until_hwa)
            or (scenario.hwa_request_s is not None and not 0 <= scenario.hwa_request_s <= scenario.duration_s)):
        raise ValueError('invalid scenario time')
    if not 0 <= scenario.start_s < sum(s.length for s in segments):
        raise ValueError('start position outside road')
    if scenario.start_s + scenario.speed_mps * scenario.duration_s > sum(s.length for s in segments):
        raise ValueError('road too short for requested run')
    return scenario


def scenario_xml(params, fault=False):
    root = document(params.get('description', params['scenario_id']))
    declarations_node = node(root, 'ParameterDeclarations')
    for key, value in params.items():
        node(declarations_node, 'ParameterDeclaration', name=key,
             parameterType='boolean' if isinstance(value, bool) else 'double' if isinstance(value, (float, int)) else 'string', value=value)
    node(root, 'CatalogLocations')
    node(node(root, 'RoadNetwork'), 'LogicFile', filepath='$road_file')
    vehicle = node(node(node(root, 'Entities'), 'ScenarioObject', name='Ego'), 'Vehicle', name='Ego', vehicleCategory='car')
    box = node(vehicle, 'BoundingBox')
    node(box, 'Center', x=1.45, y=0, z=.75)
    node(box, 'Dimensions', width=1.9, length=4.9, height=1.5)
    node(vehicle, 'Performance', maxSpeed=60, maxAcceleration=10, maxDeceleration=10)
    axles = node(vehicle, 'Axles')
    node(axles, 'FrontAxle', maxSteering=.61, wheelDiameter=.65, trackWidth=1.6, positionX=2.9, positionZ=.325)
    node(axles, 'RearAxle', maxSteering=0, wheelDiameter=.65, trackWidth=1.6, positionX=0, positionZ=.325)
    properties = node(vehicle, 'Properties')
    node(properties, 'Property', name='pp:adapter', value='single-ego-v1')
    for key in ('profile', 'acc', 'hwa_request_s', 'hold_until_hwa', 'camera_view_m', 'camera_view_start_m',
                'adas_mode', 'lka_enabled', 'elk_enabled', 'expect_intervention', 'protocol', 'hwa_view_gate',
                'expected_outcome', 'can_bus', 'realism', 'loop', *SIM_PROPERTIES_FIELDS):
        if key in params:
            node(properties, 'Property', name='pp:' + key, value='$' + key)
    story = node(root, 'Storyboard')
    actions = node(node(story, 'Init'), 'Actions')
    if fault:
        command = node(node(actions, 'UserDefinedAction'), 'CustomCommandAction', type='pp:lane_fault:v1')
        command.text = ('{"kind":"$fault_kind","start_s":$fault_start_s,"duration_s":$fault_duration_s,'
                        '"lines":$fault_lines,"value":$fault_value,"sigma_c0":$fault_sigma_c0,"sigma_c1":$fault_sigma_c1}')
    private = node(actions, 'Private', entityRef='Ego')
    pos = node(node(node(node(private, 'PrivateAction'), 'TeleportAction'), 'Position'),
               'RoadPosition', roadId='1', s='$start_s_m', t='$start_offset_m')
    node(pos, 'Orientation', type='relative', h='$start_heading_rad')
    speed = node(node(node(private, 'PrivateAction'), 'LongitudinalAction'), 'SpeedAction')
    node(speed, 'SpeedActionDynamics', dynamicsShape='step', dynamicsDimension='time', value=0)
    node(node(speed, 'SpeedActionTarget'), 'AbsoluteTargetSpeed', value='$speed_mps')
    condition = node(node(node(story, 'StopTrigger'), 'ConditionGroup'), 'Condition', name='end', delay=0, conditionEdge='none')
    node(node(condition, 'ByValueCondition'), 'SimulationTimeCondition', value='$duration_s', rule='greaterOrEqual')
    return root


def concrete(path, destination, overrides=None):
    """Bake road parameters and vehicle profile; write a portable .xosc/.xodr pair."""
    path, destination = Path(path), Path(destination)
    scenario = load_scenario(path, overrides)
    root, params = resolve(parse(path), overrides)
    road_path = destination.with_suffix('.xodr')
    output_road = road_xml(scenario.segments, scenario.lane_width)
    if scenario.road_layout is not None:
        source_path = path.parent / root.find('./RoadNetwork/LogicFile').attrib['filepath']
        source_road = parse(source_path).find('road')
        _set_road_width(source_road, scenario.lane_width)
        road = output_road.find('road')
        road.remove(road.find('lanes'))
        road.append(source_road.find('lanes'))
        objects = source_road.find('objects')
        if objects is not None:
            road.append(objects)
    write(output_road, road_path)
    root.find('./RoadNetwork/LogicFile').set('filepath', road_path.name)
    root.find('FileHeader').set('description', scenario.notes['description'])
    for p in root.findall('./ParameterDeclarations/ParameterDeclaration'):
        if p.get('name') == 'road_file':
            p.set('value', road_path.name)
        if p.get('name') in ('curvature_scale', 'direction'):
            p.set('value', '1')
    profile = PROFILES[scenario.profile]
    if scenario.driver is not None:
        positions = {p.attrib['entityRef']: p.find('./PrivateAction/TeleportAction/Position/RoadPosition')
                     for p in root.findall('./Storyboard/Init/Actions/Private')}
        positions['Ego'].set('t', text(scenario.start_offset_m))
        names = [e.attrib['name'] for e in root.findall('./Entities/ScenarioObject')[1:]]
        for name, obj in zip(names, scenario.traffic, strict=True):
            position = positions[name]
            position.set('s', text(obj.s0))
            position.set('t', text(obj.d))
    vehicle = root.find('./Entities/ScenarioObject/Vehicle')
    vehicle.set('mass', text(profile.mass))
    vehicle.find('./BoundingBox/Dimensions').set('width', text(profile.width_with_mirrors))
    vehicle.find('./BoundingBox/Center').set('x', text(profile.wheelbase / 2))
    vehicle.find('./Axles/FrontAxle').set('positionX', text(profile.wheelbase))
    vehicle.find('./Axles/FrontAxle').set('maxSteering', text(profile.max_wheel_angle))
    write(root, destination)
    return destination


# Properties a fault definition may switch on in its host (as loader.with_fault).
FAULT_FLAGS = ('pp:hwa_view_gate', 'pp:can_bus', 'pp:realism')


def inject(destination, faults, trigger=None, offset_s=0.0, sim=None):
    """Add fault definitions to a concrete host case in place (Software Qualification Test
    Specification 6: moments of injection, 6.2 combined faults).

    `faults`: [(fault file, its parameter values, name)]. Every command is copied as resolved;
    with `trigger` each timed command starts `offset_s` after that planner-output event
    (sim.faults.trigger), clock faults keep their time. Flags of the definition are switched on
    in the host, the expected outcome is the stricter of both (5.3), `sim` sets simulator
    properties (SIM_PROPERTIES_FIELDS), and pp:faults names the definitions (labels L3, L4)."""
    from eval import labels
    destination = Path(destination)
    root = parse(destination)
    actions = root.find('./Storyboard/Init/Actions')
    at = list(actions).index(actions.find('Private'))
    properties = root.find('./Entities/ScenarioObject/Vehicle/Properties')

    def prop(name):
        return next((p for p in properties.findall('Property') if p.get('name') == name), None)

    def set_prop(name, value):
        (prop(name) if prop(name) is not None else node(properties, 'Property', name=name)).set('value', text(value))

    names = [n for n in (prop('pp:faults').get('value').split(',') if prop('pp:faults') is not None else []) if n]
    for path, params, name in faults:
        froot, _ = resolve(parse(path), params)
        for command in froot.findall('./Storyboard/Init/Actions/UserDefinedAction/CustomCommandAction'):
            spec = json.loads(command.text or '{}')
            if trigger is not None and command.get('type') != 'pp:clock_fault:v1':
                spec['trigger'], spec['start_s'] = trigger, offset_s
            action = ET.Element('UserDefinedAction')
            ET.SubElement(action, 'CustomCommandAction', type=command.get('type')).text = json.dumps(
                spec, ensure_ascii=False, separators=(',', ':'))
            actions.insert(at, action)
            at += 1
        given = {p.get('name'): p.get('value') for p in froot.findall('./Entities/ScenarioObject/Vehicle/Properties/Property')}
        for flag in FAULT_FLAGS:
            if given.get(flag) == 'true':
                set_prop(flag, 'true')
        if given.get('pp:loop') == 'open':
            set_prop('pp:loop', 'open')
        if given.get('pp:expected_outcome'):
            host = prop('pp:expected_outcome')
            set_prop('pp:expected_outcome', labels.stricter(host.get('value') if host is not None else None,
                                                            given['pp:expected_outcome']))
        names.append(name)
    for field, value in (sim or {}).items():
        if field not in SIM_PROPERTIES_FIELDS:
            raise ValueError(f'unknown simulator property {field}')
        set_prop('pp:' + field, float(value))
    set_prop('pp:faults', ','.join(names))
    write(root, destination)
    return destination


@lru_cache(maxsize=2)
def _schema(kind):
    import xmlschema
    path = (SCHEMA / 'openscenario-1.3.1' / 'OpenSCENARIO.xsd' if kind == 'xosc'
            else SCHEMA / 'opendrive-1.8.1' / 'OpenDRIVE_Core.xsd')
    return xmlschema.XMLSchema11(path, allow='local')


def validate(path):
    path = Path(path)
    _schema(path.suffix.lstrip('.')).validate(path)
