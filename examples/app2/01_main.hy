(print "App2")
(setv _base_url "https://www.app2.de")


(setv username (Variable "username"))
(setv password (Variable "password"))
(setv mfa_code (Prompt "MFA"))



(setv csrf_name
      (Html
        :name "csrf_name"
        :tag "input"
        :attributes
        {:name "^[0-9A-Fa-f]{10}$"
         :value "^[0-9A-Fa-f]{64}$"
         :type "hidden"}
        :extract "name"))

(setv csrf_value
      (Html
        :name "csrf_value"
        :tag "input"
        :attributes
        {:name "^[0-9A-Fa-f]{10}$"
         :value "^[0-9A-Fa-f]{64}$"
         :type "hidden"}
        :extract "value"))



(setv session_id
      (Cookie "PHPSESSID"))
(setv init_vector
      (Cookie "iv"))
(setv verify
      (Cookie "verify"))
