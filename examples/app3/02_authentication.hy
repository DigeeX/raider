(setv initialization
      (Flow
        :name "initialization"
        :request (Request
                   :method "GET"
                   :path "about")
        :outputs [csrf_token session_id]
        :operations [(Print csrf_token session_id)
                     (Http
                       :status 200
                       :action
                       (NextStage "login")
                       :otherwise
                       (Error "Cannot initialize session"))]))

(setv login
      (Flow
        :name "login"
        :request
        (Request
          :method "POST"
          :path "auth/sign_in"
          :cookies [session_id]
          :data
          {"csrf_token" csrf_token
           "email" username
           "password" password})
        :outputs [session_id csrf_token remember_user]
        :operations [(Grep
                       :regex "Invalid Email or password"
                       :action
                       (Error "Invalid credentials"))
                     (Grep
                       :regex "Enter the two-factor code"
                       :action
                       (NextStage "multi_factor"))
                     (Http
                       :status 302
                       :action
                       (Print "Authentication successful"))]))



(setv multi_factor
      (Flow
        :name "multi_factor"
        :request
        (Request
          :method "POST"
          :path "auth/sign_in"
          :cookies [session_id remember_user]
	  :data
          {"csrf_token" csrf_token
           "otp_attempt" mfa_code})
        :outputs [csrf_token session_id remember_user]
        :operations [(Grep
                     :regex "Invalid two-factor code"
                     :action
                     (NextStage "multi_factor")
                     :otherwise
                     (Print "Authenticated successfully"))]))


(setv _authentication [initialization
                       login
                       multi_factor])
