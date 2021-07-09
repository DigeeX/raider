(print "App1")
(setv _base_url "https://app1.de/")


(setv username (Variable "username"))
(setv password (Variable "password"))

(setv session_id
      (Cookie "admin-session"))

(setv initialization
      (Flow
        :name "initialization"
        :request (Request
                   :method "GET"
                   :url "https://auth.app1.de/login")
        :operations [(Http
                       :status 200
                       :action (NextStage "login"))]))

(setv login
      (Flow
        :name "login"
        :request (Request
                   :method "POST"
                   :path "/login/session"
                   :data
                   {"password" password
                    "username" username})
        :outputs [session_id]
        :operations [(Http
                       :status 403
                       :action (Error "login error"))]))



(setv _authentication
      [initialization
       login])
