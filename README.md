# Esky
A Flask Server to run notebooks asynchronously using huey workers and store them in an esky, keeping your notebooks fresh and cool for when you need. You send it, we run it & store it.

---------
##### Esky
*(noun)* | /**eh**·skee/*ɛ*sˈki/
> An Australian brand of portable coolers. The term "esky" is also commonly used in Australia to generically refer to portable coolers or ice boxes and is part of the Australian vernacular, in place of words like "cooler" or "cooler box" and the New Zealand "chilly bin". The term derives from the word Eskimo.
- https://en.wikipedia.org/wiki/Esky

## Start the Consumer
In a new terminal, run: `python -m huey.bin.huey_consumer tasks.huey`
This will add all the tasks specificed in `task.py` for the consumer to be able to receive and execute.

## Start the App
In the terminal, run: `python esky.py`
This will serve the app, which you can then post to to run notebooks
e.g.
Send a POST request to `http://localhost:5000/run/`
Body is raw JSON
`{"input_notebook": "path/to/examples/add.ipynb", "parameters": {"your": "params"}, "kernel_name": "your_kernel"}`