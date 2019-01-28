"Simple parser for Garmin TCX files."

import time
from lxml import objectify

namespace = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'


class TCXParser:

    def __init__(self, tcx_file):
        tree = objectify.parse(tcx_file)
        self.root = tree.getroot()
        self.activity = self.root.Activities.Activity

    def hr_values(self):
        return [int(x.text) for x in self.root.xpath('//ns:HeartRateBpm/ns:Value', namespaces={'ns': namespace})]

    def latitude_values(self):
        return [float(x.text) for x in self.root.xpath('//ns:Position/ns:LatitudeDegrees', namespaces={'ns': namespace})]

    def longitude_values(self):
        return [float(x.text) for x in self.root.xpath('//ns:Position/ns:LongitudeDegrees', namespaces={'ns': namespace})]

    def altitude_points(self):
        return [float(x.text) for x in self.root.xpath('//ns:AltitudeMeters', namespaces={'ns': namespace})]

    def time_values(self):
        return [x.text for x in self.root.xpath('//ns:Time', namespaces={'ns': namespace})]

    def cadence_values(self):
        return [int(x.text) for x in self.root.xpath('//ns:Cadence', namespaces={'ns': namespace})]

    @property
    def creator(self):
        if hasattr(self.activity, 'Creator'):
            return self.activity.Creator.Name.pyval

    @property
    def creator_version(self):
        if hasattr(self.activity, 'Creator'):
            return self.activity.Creator.UnitId.pyval

    @property
    def start_latitude(self):
        latitude_data = self.latitude_values()
        if len(latitude_data) > 0:
            return latitude_data[0]

    @property
    def start_longitude(self):
        longitude_data = self.longitude_values()
        if len(longitude_data) > 0:
            return longitude_data[0]

    @property
    def end_latitude(self):
        latitude_data = self.latitude_values()
        if len(latitude_data) > 0:
            return latitude_data[-1]

    @property
    def end_longitude(self):
        longitude_data = self.longitude_values()
        if len(longitude_data) > 0:
            return longitude_data[-1]

    @property
    def activity_type(self):
        return self.activity.attrib['Sport'].lower()

    @property
    def started_at(self):
        return self.activity.Lap.Track.Trackpoint.Time.pyval

    @property
    def completed_at(self):
        return self.activity.Lap[-1].Track.Trackpoint[-1].Time.pyval

    @property
    def cadence_avg(self):
        return getattr(self.activity.Lap[-1], 'Cadence', None)

    @property
    def cadence_max(self):
      """Returns max cadence of workout"""
      cadence_data = self.cadence_values()
      if len(cadence_data) > 0:
          return max(cadence_data)

    @property
    def speed_max(self):
        return self.activity.Lap[-1].MaximumSpeed

    @property
    def distance(self):
        distance_values = self.root.findall('.//ns:DistanceMeters', namespaces={'ns': namespace})
        if distance_values:
            return distance_values[-1]

    @property
    def distance_units(self):
        return 'meters'

    @property
    def duration(self):
        """Returns duration of workout in seconds."""
        duration = sum(lap.TotalTimeSeconds if hasattr(lap, 'TotalTimeSeconds') else 0  for lap in self.activity.Lap)
        if duration > 0:
            return duration

    @property
    def calories(self):
        total_calories = sum(lap.Calories if hasattr(lap, 'Calories') else 0 for lap in self.activity.Lap)
        if total_calories > 0:
            return total_calories

    @property
    def hr_avg(self):
        """Average heart rate of the workout"""
        hr_data = self.hr_values()
        if len(hr_data) > 0:
            return sum(hr_data)/len(hr_data)

    @property
    def hr_max(self):
        hr_data = self.hr_values()
        if len(hr_data) > 0:
            return max(hr_data)

    @property
    def hr_min(self):
        """Minimum heart rate of the workout"""
        return min(self.hr_values())

    @property
    def pace(self):
        """Average pace (mm:ss/km for the workout"""
        secs_per_km = self.duration/(self.distance/1000)
        return time.strftime('%M:%S', time.gmtime(secs_per_km))

    @property
    def altitude_avg(self):
        """Average altitude for the workout"""
        altitude_data = self.altitude_points()
        if len(altitude_data) > 0:
            return sum(altitude_data)/len(altitude_data)

    @property
    def altitude_max(self):
        """Max altitude for the workout"""
        altitude_data = self.altitude_points()
        return max(altitude_data)

    @property
    def altitude_min(self):
        """Min altitude for the workout"""
        altitude_data = self.altitude_points()
        return min(altitude_data)

    @property
    def ascent(self):
        """Returns ascent of workout in meters"""
        total_ascent = 0.0
        altitude_data = self.altitude_points()
        for i in range(len(altitude_data) - 1):
            diff = altitude_data[i+1] - altitude_data[i]
            if diff > 0.0:
                total_ascent += diff
        return total_ascent

    @property
    def descent(self):
        """Returns descent of workout in meters"""
        total_descent = 0.0
        altitude_data = self.altitude_points()
        for i in range(len(altitude_data) - 1):
            diff = altitude_data[i+1] - altitude_data[i]
            if diff < 0.0:
                total_descent += abs(diff)
        return total_descent
