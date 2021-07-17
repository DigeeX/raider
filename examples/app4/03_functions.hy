(setv nickname
      (Regex
        :name "nickname"
        :regex "href=\"/user/([^\"]+)"))

(setv get_unread_messages
      (Flow
        :name "get_unread_messages"
        :request (Request
                   :method "GET"
                   :headers [(Header.bearerauth access_token)]
                   :url "https://www.app4.com/unread_message_count")))

(setv get_nickname
      (Flow
        :name "get_nickname"
        :request (Request
                   :method "GET"
                   :cookies [session_id app_session]
                   :path "/")
        :outputs [nickname]
        :operations [(Print nickname)]))

(setv _functions [get_unread_messages
                  get_nickname])
