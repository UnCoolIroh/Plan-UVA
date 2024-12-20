class User:
    def __init__(username, google_account):
        self.username = username
        self.google_account = google_account # unsure of how google API works so this may be useless later on
        self.type = "COMMON"
        self.inbox = []
        self.projects = []
    
    def get_username():
        return self.username
    
    def get_type():
        return self.type

    def get_inbox():
        return self.inbox
    
    def get_projects():
        return self.projects

    def is_admin():
        return self.type.equals("ADMIN")
    