(print "App4")
(setv _base_url "https://www.app4.com/")


;; Only inputs
(setv username (Variable "username"))
(setv password (Variable "password"))
(setv mfa_code (Prompt "MFA"))

;; both inputs/outputs
(setv csrf_token
      (Html
        :name "csrf_token"
        :tag "input"
        :attributes
        {:name "csrf_token"
         :value "^[0-9a-f]{40}$"
         :type "hidden"}
        :extract "value"))

(setv access_token
      (Regex
        :name "access_token"
        :regex "\"accessToken\":\"([^\"]+)\""))

(setv session_id (Cookie "session"))
(setv app_session (Cookie "app_session"))
