I think I should expand the functionality of this thing. First of all, since the main inference pipeline is ready, only thing left is making it into a service and decide on the potential functionalities.

Now I'm thinking of three functionalities:

1. our first one, we ask what's wrong with smth (usually direct command etc)

2. our second one, we ask but in a bit of detail, usually how to do something

3. we fuck up the command and get an error, then we can't remember the correct usage, so we use this and it works out (hopefully)



I think (1) and (2) can be a single "ask" command, where the (3) should be a separate thing since it's gonna ingest the previous command and previous command's stdout.



for the (3), we need to be able to listen to the terminal output and then use a specifically constructed context so the model would know the error + context.
