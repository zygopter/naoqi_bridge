#!/usr/bin/env python
# Copyright (C) 2014 Aldebaran Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from distutils.version import LooseVersion

import rospy

from octomap_msgs.msg import Octomap

from nao_driver import NaoNode
from nao_driver.boost.octomap_python import octomap_str_to_tuple

class NaoOctomap(NaoNode):
    def __init__(self):
        NaoNode.__init__(self, 'nao_octomap')

        if self.get_version() < LooseVersion('2.0'):
            rospy.loginfo('NAOqi version < 2.0, Octomap is not used')
            exit(0)

        proxy = self.get_proxy("ALNavigation")
        if proxy is None:
            rospy.loginfo('Could not get access to the ALNavigation proxy')
            exit(1)
        proxy._setObstacleModeForSafety(1)

        # Create ROS publisher
        self.pub = rospy.Publisher("octomap", Octomap, latch = True, queue_size=1)

        self.fps = 1

        rospy.loginfo("nao_octomap initialized")

    def run(self):
        r = rospy.Rate(self.fps)
        octomap = Octomap()
        octomap.header.frame_id = '/odom'

        while self.is_looping():
            octomap_bin = self.get_proxy("ALNavigation")._get3DMap()
            octomap.binary, octomap.id, octomap.resolution, octomap.data = octomap_str_to_tuple(octomap_bin)

            octomap.header.stamp = rospy.Time.now()

            self.pub.publish(octomap)

            r.sleep()

if __name__ == '__main__':
    nao_octomap = NaoOctomap()
    nao_octomap.start()
    rospy.spin()
