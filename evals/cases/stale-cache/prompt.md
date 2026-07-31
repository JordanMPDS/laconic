We set the feature-flag cache TTL to 60 seconds, but a flag change still takes
up to an hour to reach some users. flags.js is the client every service uses,
and response-headers.txt is what the flag service actually returns. Read them
and tell me why it is still an hour. Don't edit anything.
