# Where this runs

Every file under `api/` is deployed as an independent serverless function.
There is no long-lived server process and no way to obtain one on this plan.

Constraints that come from the platform, not from us:

- A function invocation is killed at **10 seconds**. There is no extension.
- **Connection upgrades are not proxied.** A WebSocket handshake against any
  `api/` path returns 501 at the edge; the request never reaches our code.
- There is no sticky routing. Two requests from the same browser reach two
  different instances, and instances share no memory.
- Instances are frozen between invocations, so a timer or subscription started
  during a request does not keep running after the response is sent.

Moving off this platform is not on the roadmap. The last review priced it at a
quarter of engineering time and it was declined.
