class GroupsClient:
    def __init__(self, http):
        self.http = http

    def create(self, org_name):
        resp = self.http.post(
            "/groups/api/create_group", 
            json={
                "org_name": org_name
            }
        )
        return resp

    def transfer(self, org_name, new_owner_email):
        resp = self.http.post(
            "/groups/api/transfer_group", 
            json={
                "org_name": org_name,
                "new_owner_email": new_owner_email
            }
        )
        return resp

    def shut(self, org_name):
        resp = self.http.post(
            "/groups/api/shut_group", 
            json={
                "org_name": org_name
            }
        )
        return resp

    def leave(self, org_name):
        resp = self.http.post(
            "/groups/api/leave_group", 
            json={
                "org_name": org_name
            }
        )
        return resp

    def promote(self, org_name, new_admin_email):
        resp = self.http.post(
            "/groups/api/add_admin", 
            json={
                "org_name": org_name,
                "new_admin_email": new_admin_email
            }
        )
        return resp

    def demote(
            self, 
            org_name,
            admin_email
        ):
        resp = self.http.post(
            "/groups/api/remove_admin", 
            json={
                "org_name": org_name,
                "admin_email": admin_email
            }
        )
        return resp

    def invite(self, org_name, new_member_email, duration):
        resp = self.http.post(
            "/groups/api/invite_member", 
            json={
                "org_name": org_name,
                "new_member_email": new_member_email,
                "duration": duration
            }
        )
        return resp

    def join(self, org_name):
        resp = self.http.post(
            "/groups/api/join_group", 
            json={
                "org_name": org_name,
            }
        )
        return resp
    
    def adjust_permissions(
            self, 
            org_name,
            member_email,
            create_permission,
            sign_permission,
            export_permission
        ):
        resp = self.http.post(
            "/groups/api/adjust_member_permission", 
            json={
                "org_name": org_name,
                "member_email": member_email,
                "create_permission": create_permission,
                "sign_permission": sign_permission,
                "export_permission": export_permission
            }
        )
        return resp

    def revoke(self, org_name, member_email):
        resp = self.http.post(
            "/groups/api/revoke_membership", 
            json={
                "org_name": org_name,
                "member_email": member_email
            }
        )
        return resp
    
    def groups(self):
        resp = self.http.get("/groups/api/groups")
        return resp
    
    def members(self, org_name):
        resp = self.http.post(
            "/groups/api/members", 
            json={
                "org_name": org_name
            }
        )
        return resp

    def permissions(self, org_name):
        resp = self.http.post(
            "/groups/api/permissions", 
            json={
                "org_name": org_name
            }
        )
        return resp