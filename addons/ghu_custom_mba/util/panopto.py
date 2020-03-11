from zeep import Client
import hashlib
import uuid
import logging
import zeep

_logger = logging.getLogger(__name__)

class GhuPanopto():

    def __init__(self, env):
        self.userkey = env['ir.config_parameter'].sudo().get_param('ghu.panopto_user')
        self.password = env['ir.config_parameter'].sudo().get_param('ghu.panopto_password')
        self.servername = env['ir.config_parameter'].sudo().get_param('ghu.panopto_server')
        self.applicationkey = ''
        self.sessionClient = Client("https://" + self.servername +
                                    "/Panopto/PublicAPI/4.6/SessionManagement.svc?wsdl")
        self.accessClient = Client("https://" + self.servername +
                                   "/Panopto/PublicAPI/4.6/AccessManagement.svc?wsdl")
        self.userClient = Client(
            "https://" + self.servername + "/Panopto/PublicAPI/4.6/UserManagement.svc?wsdl")
        self.authInfo = {'AuthCode': self.generateauthcode(self.userkey, self.servername, self.applicationkey),
                         'Password': self.password, 'UserKey': self.userkey}

    def generateauthcode(self, userkey, servername, sharedSecret):
        payload = userkey + '@' + servername
        signedPayload = payload + '|' + sharedSecret
        m = hashlib.sha1()
        m.update(signedPayload.encode('utf-8'))
        authcode = m.hexdigest().upper()
        return authcode

    def createFolder(self, name, externalId, isPublic=False, parentFolder=None):
        folders = self.sessionClient.service.GetFoldersByExternalId(auth=self.authInfo, folderExternalIds=[externalId])
        if not folders:
            folder = self.sessionClient.service.AddFolder(
                auth=self.authInfo, name=name, parentFolder=parentFolder, isPublic=isPublic)
            self.sessionClient.service.UpdateFolderExternalId(
                auth=self.authInfo, folderId=folder.Id, externalId=externalId)
        else:
            return folders[0].Id
        return folder.Id


    def activateAssignmentFolder(self, folder):
        #TODO: Find correct method to activate dropbox
        folder = self.sessionClient.service.ActivateDropbox(
            auth=self.authInfo, name=name)
        return folder.Id


    # Role can be either Viewer, Creator or Publisher
    def grantAccessToFolder(self, folder, userIds, role='Viewer'):
        roleFactory = self.accessClient.type_factory('ns2')
        role = roleFactory.AccessRole(role)
        try:
            self.accessClient.service.GrantUsersAccessToFolder(auth=self.authInfo, folderId=folder, userIds=userIds, role=role)
        except zeep.exceptions.Fault as error:
            _logger.info(error.detail)
    
    # Role can be either Viewer, Creator or Publisher
    def grantAccessToSession(self, session, userIds):
        try:
            self.accessClient.service.GrantUsersViewerAccessToSession(auth=self.authInfo, sessionId=session, userIds=userIds)
        except zeep.exceptions.Fault as error:
            _logger.info(error.detail)

    # Role can be either Viewer, Creator or Publisher
    def revokeAccessToFolder(self, folder, userIds, role='Viewer'):
        roleFactory = self.accessClient.type_factory('ns2')
        role = roleFactory.AccessRole(role)
        self.accessClient.service.RevokeUsersAccessFromFolder(
            auth=self.authInfo, folderId=folder, userIds=userIds, role=role)

    # User Management

    def getUserId(self, user):
        panoptoUser = self.userClient.service.GetUserByKey(auth = self.authInfo, userKey='Odoo\\'+str(user.id))
        if panoptoUser.Email:
            return panoptoUser.UserId
        else:
            return self.createUser(user)

    def createUser(self, user):
        userFactory = self.userClient.type_factory('ns2')
        user = userFactory.User(user.email, False, user.firstname, [], user.lastname, None, None, None, 'Odoo\\'+str(user.id), None)
        panoptoUser = self.userClient.service.CreateUser(auth = self.authInfo, user=user, initialPassword='')
        if panoptoUser:
            return panoptoUser
        else:
            return None

    
    def getFirstSessionOfFolder(self, folderId):
        sessions = self.sessionClient.service.GetSessionsList(auth=self.authInfo, request={'FolderId':folderId})
        if sessions.TotalNumberResults > 0:
            return sessions.Results.Session[0]
        return False