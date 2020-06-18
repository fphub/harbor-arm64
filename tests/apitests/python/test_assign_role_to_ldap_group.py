# coding: utf-8

"""
    Harbor API

    These APIs provide services for manipulating Harbor project.  

    OpenAPI spec version: 1.4.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import
import os
import sys
sys.path.append(os.environ["SWAGGER_CLIENT_PATH"])

import unittest
import testutils
import docker

import swagger_client
from swagger_client.models.project import Project 
from swagger_client.models.project_req import ProjectReq  
from swagger_client.models.project_metadata import ProjectMetadata  
from swagger_client.models.project_member import ProjectMember 
from swagger_client.models.user_group import UserGroup  
from swagger_client.models.configurations import Configurations  


from swagger_client.rest import ApiException
from pprint import pprint

#Testcase
#3-07-LDAP usergroup manage project group members
class TestAssignRoleToLdapGroup(unittest.TestCase):
    harbor_host = os.environ["HARBOR_HOST"]
    """AssignRoleToLdapGroup unit test stubs"""
    product_api = testutils.GetProductApi("admin", "Harbor12345")
    project_id = 0
    docker_client = docker.from_env()
    
    def setUp(self):
        #login with admin, create a project and assign role to ldap group
        result = self.product_api.configurations_put(configurations=Configurations(ldap_filter="", ldap_group_attribute_name="cn", ldap_group_base_dn="ou=groups,dc=example,dc=com", ldap_group_search_filter="objectclass=groupOfNames", ldap_group_search_scope=2))
        pprint(result)
        cfgs = self.product_api.configurations_get()
        pprint(cfgs)
        req = ProjectReq() 
        req.project_name = "ldap_group_test_prj"
        req.metadata = ProjectMetadata(public="false")
        result = self.product_api.projects_post(req)
        pprint(result)

        projs = self.product_api.projects_get(name="ldap_group_test_prj")
        if projs.count>0 :
            project = projs[0]
            self.project_id = project.project_id
        
        # asign role to project with dn
        group_dn = "cn=harbor_admin,ou=groups,dc=example,dc=com"
        projectmember = ProjectMember()
        projectmember.role_id = 1
        projectmember.member_group = UserGroup(ldap_group_dn=group_dn)

        result = self.product_api.projects_project_id_members_post( project_id=self.project_id, project_member=projectmember )
        pprint(result)

        group_dn = "cn=harbor_dev,ou=groups,dc=example,dc=com"
        projectmember = ProjectMember()
        projectmember.role_id = 2
        projectmember.member_group = UserGroup(ldap_group_dn=group_dn)

        result = self.product_api.projects_project_id_members_post( project_id=self.project_id, project_member=projectmember )
        pprint(result)

        group_dn = "cn=harbor_guest,ou=groups,dc=example,dc=com"
        projectmember = ProjectMember()
        projectmember.role_id = 3
        projectmember.member_group = UserGroup(ldap_group_dn=group_dn)

        result = self.product_api.projects_project_id_members_post( project_id=self.project_id, project_member=projectmember )
        pprint(result)
        pass

    def tearDown(self):
        #delete images in project
        result = self.product_api.repositories_repo_name_delete(repo_name="ldap_group_test_prj/busybox")
        pprint(result)
        result = self.product_api.repositories_repo_name_delete(repo_name="ldap_group_test_prj/busyboxdev")
        pprint(result)
        if self.project_id > 0 :
              self.product_api.projects_project_id_delete(self.project_id)
        pass

    def testAssignRoleToLdapGroup(self):
        """Test AssignRoleToLdapGroup"""
        admin_product_api = testutils.GetProductApi(username="admin_user", password="zhu88jie")
        projects = admin_product_api.projects_get(name="ldap_group_test_prj")
        self.assertTrue(projects.count > 1)
        self.assertEqual(1, projects[0].current_user_role_id)
       

        dev_product_api = testutils.GetProductApi("dev_user", "zhu88jie")
        projects = dev_product_api.projects_get(name="ldap_group_test_prj")
        self.assertTrue(projects.count > 1)
        self.assertEqual(2, projects[0].current_user_role_id)

        guest_product_api = testutils.GetProductApi("guest_user", "zhu88jie")
        projects = guest_product_api.projects_get(name="ldap_group_test_prj")
        self.assertTrue(projects.count > 1)
        self.assertEqual(3, projects[0].current_user_role_id)        

        self.dockerCmdLoginAdmin(username="admin_user", password="zhu88jie")
        self.dockerCmdLoginDev(username="dev_user", password="zhu88jie")
        self.dockerCmdLoginGuest(username="guest_user", password="zhu88jie")

        self.assertTrue(self.queryUserLogs(username="admin_user", password="zhu88jie")>0, "admin user can see logs")
        self.assertTrue(self.queryUserLogs(username="dev_user", password="zhu88jie")>0, "dev user can see logs")
        self.assertTrue(self.queryUserLogs(username="guest_user", password="zhu88jie")>0, "guest user can see logs")
        self.assertTrue(self.queryUserLogs(username="test", password="123456")==0, "test user can not see any logs")

        pass

    # admin user can push, pull images
    def dockerCmdLoginAdmin(self, username, password):
        pprint(self.docker_client.info())
        self.docker_client.login(username=username, password=password, registry=self.harbor_host)   
        self.docker_client.images.pull("busybox:latest")
        image = self.docker_client.images.get("busybox:latest")
        image.tag(repository=self.harbor_host+"/ldap_group_test_prj/busybox", tag="latest")
        output = self.docker_client.images.push(repository=self.harbor_host+"/ldap_group_test_prj/busybox", tag="latest") 
        if output.find("error")>0 :
            self.fail("Should not fail to push image for admin_user")
        self.docker_client.images.pull(repository=self.harbor_host+"/ldap_group_test_prj/busybox", tag="latest")
        pass
    # dev user can push, pull images
    def dockerCmdLoginDev(self, username, password, harbor_server=harbor_host):
        self.docker_client.login(username=username, password=password, registry=self.harbor_host)   
        self.docker_client.images.pull("busybox:latest")
        image = self.docker_client.images.get("busybox:latest")
        image.tag(repository=self.harbor_host+"/ldap_group_test_prj/busyboxdev", tag="latest")
        output = self.docker_client.images.push(repository=self.harbor_host+"/ldap_group_test_prj/busyboxdev", tag="latest") 
        if output.find("error") >0 :
            self.fail("Should not fail to push images for dev_user")
        pass
    # guest user can pull images
    def dockerCmdLoginGuest(self, username, password, harbor_server=harbor_host):
        self.docker_client.login(username=username, password=password, registry=self.harbor_host)   
        self.docker_client.images.pull("busybox:latest")
        image = self.docker_client.images.get("busybox:latest")
        image.tag(repository=self.harbor_host+"/ldap_group_test_prj/busyboxguest", tag="latest")
        output = self.docker_client.images.push(repository=self.harbor_host+"1/ldap_group_test_prj/busyboxguest", tag="latest") 
        if output.find("error")<0 :
            self.fail("Should failed to push image for guest user")
        self.docker_client.images.pull(repository=self.harbor_host+"/ldap_group_test_prj/busybox", tag="latest")
        pass        
    # check can see his log in current project
    def queryUserLogs(self, username, password, harbor_host=harbor_host):
        client_product_api = testutils.GetProductApi(username=username, password=password)
        logs = client_product_api.logs_get(repository="ldap_group_test_prj", username=username)
        if logs == None:
            return 0
        else:
            return logs.count

if __name__ == '__main__':
    unittest.main()
