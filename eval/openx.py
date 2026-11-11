"""ASAM XML adapter for the supported single-ego benchmark subset.

OpenSCENARIO 1.3.1; OpenDRIVE 1.8.1. This is deliberately not a general
OpenSCENARIO interpreter. Simulator-specific behavior uses pp:* extensions.
"""
from copy import deepcopy
from functools import lru_cache
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import numpy as np

from sim.faults.lane import LaneFault
from sim.scenario import Scenario
from sim.vehicle.profiles import PROFILES
from sim.world.road import Segment

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'benchmark' / 'schema'
TOKEN = re.compile(r'\$([A-Za-z_][A-Za-z0-9_]*)')


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


def anchors(path):
    """Named, coupled assignments. Anchor IDs never depend on list position."""
    root = parse(Path(path).with_suffix('.anchors.xosc'))
    reference = root.find('./ParameterValueDistribution/ScenarioFile')
    if reference is None or reference.get('filepath') != Path(path).name:
        raise ValueError('anchor distribution references the wrong scenario')
    result = {}
    for values in root.findall('.//ParameterValueSet'):
        params = {p.attrib['parameterRef']: p.attrib['value'] for p in values}
        key = params['variant']
        if key in result:
            raise ValueError(f'duplicate anchor {key}')
        result[key] = params
    return result


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


def read_road(path):
    root = parse(path)
    allowed = {'OpenDRIVE', 'header', 'road', 'planView', 'geometry', 'line', 'arc',
               'spiral', 'lanes', 'laneOffset', 'laneSection', 'center', 'right',
               'lane', 'width', 'roadMark'}
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
    lanes = road.find('lanes')
    if lanes is None or len(lanes.findall('laneSection')) != 1 or len(lanes.findall('laneOffset')) != 1:
        raise ValueError('one lane section and offset required')
    section = lanes.find('laneSection')
    rights = section.findall('./right/lane')
    if number(section.attrib['s']) != 0 or [r.get('id') for r in rights] != ['-1', '-2', '-3']:
        raise ValueError('expected three right driving lanes starting at zero')
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
    if not math.isclose(number(offset.attrib['a']), 1.5 * widths[0]):
        raise ValueError('ego lane -2 must be centred on reference line')
    # The sensor model has fixed marking types and no elevation/banking. Reject
    # lane content that it cannot reproduce instead of discarding it.
    expected_lanes = road_xml(segments, widths[0]).find('road/lanes')
    def signature(element):
        def value(v):
            try:
                return number(v)
            except ValueError:
                return v
        return (element.tag, sorted((k, value(v)) for k, v in element.attrib.items()),
                [signature(child) for child in element])
    if signature(lanes) != signature(expected_lanes):
        raise ValueError('unsupported lane layout or road markings')
    return tuple(segments), widths[0]


def fault_from_command(command):
    if command.get('type') != 'pp:lane_fault:v1':
        raise ValueError(f'unsupported custom command {command.get("type")}')
    spec = json.loads(command.text or '{}')
    if spec.get('duration_s') == -1:
        spec['duration_s'] = None
    spec['lines'] = tuple(spec['lines'])
    fault = LaneFault(**spec)
    if (fault.start_s < 0 or (fault.duration_s is not None and fault.duration_s <= 0)
            or not fault.lines or any(i not in (0, 1, 2, 3) for i in fault.lines)
            or fault.sigma_c0 < 0 or fault.sigma_c1 < 0
            or (fault.kind == 'fade_line' and fault.value <= 0)):
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
    if len(objects) != 1 or objects[0].get('name') != 'Ego':
        raise ValueError('only one Ego entity is supported')
    properties = {p.get('name'): p.get('value') for p in root.findall('./Entities/ScenarioObject/Vehicle/Properties/Property')}
    if set(properties) != {'pp:adapter', 'pp:profile', 'pp:acc', 'pp:hwa_request_s', 'pp:hold_until_hwa'}:
        raise ValueError('unsupported or missing simulator properties')
    if properties.get('pp:adapter') != 'single-ego-v1':
        raise ValueError('missing pp:adapter single-ego-v1')
    if properties['pp:profile'] not in PROFILES or properties['pp:acc'] not in ('off', 'on', 'ignore_limits'):
        raise ValueError('unknown profile or ACC mode')
    privates = root.findall('./Storyboard/Init/Actions/Private')
    if len(privates) != 1 or privates[0].get('entityRef') != 'Ego':
        raise ValueError('expected Ego initial actions')
    actions = privates[0].findall('PrivateAction')
    if len(actions) != 2 or actions[0].find('TeleportAction') is None or actions[1].find('LongitudinalAction/SpeedAction') is None:
        raise ValueError('only initial teleport and absolute speed are supported')
    position = root.find('.//TeleportAction/Position/RoadPosition')
    speed = root.find('.//SpeedActionTarget/AbsoluteTargetSpeed')
    stop = root.find('./Storyboard/StopTrigger/ConditionGroup/Condition/ByValueCondition/SimulationTimeCondition')
    if position is None or speed is None or stop is None or position.get('roadId') != '1':
        raise ValueError('road position, absolute speed and time stop required')
    dynamics = root.find('.//SpeedActionDynamics')
    if dynamics is None or dynamics.get('dynamicsShape') != 'step' or dynamics.get('dynamicsDimension') != 'time' or number(dynamics.get('value')) != 0:
        raise ValueError('only instantaneous initial speed supported')
    groups = root.findall('./Storyboard/StopTrigger/ConditionGroup')
    conditions = root.findall('./Storyboard/StopTrigger/ConditionGroup/Condition')
    if len(groups) != 1 or len(conditions) != 1 or conditions[0].get('conditionEdge') != 'none' or number(conditions[0].get('delay')) != 0:
        raise ValueError('only one immediate simulation time stop supported')
    if stop.get('rule') != 'greaterOrEqual':
        raise ValueError('only greaterOrEqual time stop supported')
    road_file = root.find('./RoadNetwork/LogicFile')
    segments, width = read_road(path.parent / road_file.attrib['filepath'])
    scale = number(params.get('curvature_scale', 1))
    direction = number(params.get('direction', 1))
    if scale <= 0 or direction not in (-1, 1):
        raise ValueError('positive curvature_scale and direction +/-1 required')
    segments = tuple(Segment(s.kind, s.length, s.curvature_end * scale * direction) for s in segments)
    width = number(params.get('lane_width_m', width))
    faults = tuple(fault_from_command(c) for c in root.findall('./Storyboard/Init/Actions/UserDefinedAction/CustomCommandAction'))
    orientation = position.find('Orientation')
    if orientation is None or orientation.get('type') != 'relative' or any(number(orientation.get(k, 0)) != 0 for k in ('p', 'r')):
        raise ValueError('relative road orientation required')
    hold = properties['pp:hold_until_hwa']
    if hold not in ('true', 'false'):
        raise ValueError('invalid hold_until_hwa')
    scenario = Scenario(
        name=params['scenario_id'] + params['variant'], segments=segments, lane_width=width,
        speed_mps=number(speed.attrib['value']), profile=properties['pp:profile'],
        duration_s=number(stop.attrib['value']), hwa_request_s=number(properties['pp:hwa_request_s']),
        start_s=number(position.attrib['s']), start_offset_m=number(position.attrib['t']),
        start_heading_rad=number(orientation.attrib['h']), hold_until_hwa=hold == 'true',
        acc=properties['pp:acc'], lane_faults=faults,
        notes={'description': params.get('description', '')})
    if not 2.5 <= width <= 5.5 or not 0 <= scenario.speed_mps <= 130 / 3.6 + 1e-10:
        raise ValueError('lane width or speed outside benchmark ODD')
    if scenario.duration_s <= 0 or not 0 <= scenario.hwa_request_s <= scenario.duration_s:
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
    for key in ('profile', 'acc', 'hwa_request_s', 'hold_until_hwa'):
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
    write(road_xml(scenario.segments, scenario.lane_width), road_path)
    root.find('./RoadNetwork/LogicFile').set('filepath', road_path.name)
    root.find('FileHeader').set('description', scenario.notes['description'])
    for p in root.findall('./ParameterDeclarations/ParameterDeclaration'):
        if p.get('name') == 'road_file':
            p.set('value', road_path.name)
        if p.get('name') in ('curvature_scale', 'direction'):
            p.set('value', '1')
    profile = PROFILES[scenario.profile]
    vehicle = root.find('./Entities/ScenarioObject/Vehicle')
    vehicle.set('mass', text(profile.mass))
    vehicle.find('./BoundingBox/Dimensions').set('width', text(profile.width_with_mirrors))
    vehicle.find('./BoundingBox/Center').set('x', text(profile.wheelbase / 2))
    vehicle.find('./Axles/FrontAxle').set('positionX', text(profile.wheelbase))
    vehicle.find('./Axles/FrontAxle').set('maxSteering', text(profile.max_wheel_angle))
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
