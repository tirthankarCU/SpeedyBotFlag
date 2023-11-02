# 'SpeedyFlagBot' : Real-time low latency comment classification and flagging service.

- We aim to build a scalable service hosted on the cloud that will provide a low-latency text classification and flagging service for various social
media sites like Twitter, Facebook, etc.

- To protect people from vulgarity and blasphemy a user’s post won’t be visible unless it passes the standards imposed by our initial risk averse
flagging model.

- To make our application low latency we use a simple risk averse model for initial checks and later on use a better time consuming model to
classify the safety of a user post.

High Level Design.
![picture of high level design.](http://url/to/img.png)
