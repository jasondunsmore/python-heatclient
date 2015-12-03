#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import mock

from openstackclient.common import exceptions as exc

from heatclient import exc as heat_exc
from heatclient.osc.v1 import orchestration
from heatclient.tests.unit.osc.v1 import fakes as orchestration_fakes
from heatclient.v1 import resource_types


class TestOrchestration(orchestration_fakes.TestOrchestrationv1):
    def setUp(self):
        super(TestOrchestration, self).setUp()
        self.mock_client = self.app.client_manager.orchestration


class TestOrchestrationResourceShow(TestOrchestration):

    def setUp(self):
        super(TestOrchestrationResourceShow, self).setUp()
        self.cmd = orchestration.OrchestrationResourceShow(self.app, None)
        self.mock_client.resource_types.get = mock.Mock(
            return_value={})
        self.mock_client.resource_types.generate_template = mock.Mock(
            return_value={})

    def test_orchestration_resource_show(self):
        arglist = ['OS::Heat::None']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.resource_types.get.assert_called_once_with(
            'OS::Heat::None')

    def test_orchestration_resource_show_yaml(self):
        arglist = ['OS::Heat::None',
                   '--format', 'yaml']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.resource_types.get.assert_called_once_with(
            'OS::Heat::None')

    def test_orchestration_resource_show_error_get(self):
        arglist = ['OS::Heat::None']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.resource_types.get = mock.Mock(
            side_effect=heat_exc.HTTPNotFound)
        self.assertRaises(exc.CommandError, self.cmd.take_action, parsed_args)

    def test_orchestration_resource_show_error_template(self):
        arglist = ['OS::Heat::None',
                   '--template-type', 'hot']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.resource_types.generate_template = mock.Mock(
            side_effect=heat_exc.HTTPNotFound)
        self.assertRaises(exc.CommandError, self.cmd.take_action, parsed_args)

    def test_orchestration_resource_show_template_hot(self):
        arglist = ['OS::Heat::None',
                   '--template-type', 'hot']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.resource_types.generate_template.assert_called_with(
            **{'resource_type': 'OS::Heat::None',
               'template_type': 'hot'})

    def test_orchestration_resource_show_template_cfn(self):
        arglist = ['OS::Heat::None',
                   '--template-type', 'cfn']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.resource_types.generate_template.assert_called_with(
            **{'resource_type': 'OS::Heat::None',
               'template_type': 'cfn'})

    def test_orchestration_resource_show_template_cfn_yaml(self):
        arglist = ['OS::Heat::None',
                   '--template-type', 'cfn',
                   '--format', 'yaml']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.resource_types.generate_template.assert_called_with(
            **{'resource_type': 'OS::Heat::None',
               'template_type': 'cfn'})

    def test_orchestration_resource_show_invalid_template_type(self):
        arglist = ['OS::Heat::None',
                   '--template-type', 'abc']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.assertRaises(exc.CommandError, self.cmd.take_action, parsed_args)


class TestOrchestrationResourceList(TestOrchestration):

    expected_columns = ['Resource Type']
    list_response = [
        resource_types.ResourceType(None, 'BBB'),
        resource_types.ResourceType(None, 'AAA'),
        resource_types.ResourceType(None, 'CCC')
    ]
    expected_rows = [
        ['AAA'],
        ['BBB'],
        ['CCC']
    ]

    def setUp(self):
        super(TestOrchestrationResourceList, self).setUp()
        self.cmd = orchestration.OrchestrationResourceList(self.app, None)
        self.mock_client.resource_types.list = mock.Mock(
            return_value=self.list_response)

    def test_orchestration_resource_list(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, rows = self.cmd.take_action(parsed_args)

        self.mock_client.resource_types.list.assert_called_with(
            filters={})
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_rows, rows)

    def test_orchestration_resource_list_filter(self):
        arglist = ['--filter', 'name=B']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, rows = self.cmd.take_action(parsed_args)

        self.mock_client.resource_types.list.assert_called_once_with(
            filters={'name': 'B'})
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_rows, rows)

    def test_orchestration_resource_list_filters(self):
        arglist = ['--filter', 'name=B', '--filter', 'version=123']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, rows = self.cmd.take_action(parsed_args)

        self.mock_client.resource_types.list.assert_called_once_with(
            filters={'name': 'B', 'version': '123'})
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_rows, rows)
