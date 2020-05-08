# Esky
A Flask Server to run notebooks asynchronously using huey workers and store them in an esky, keeping your notebooks fresh and cool for when you need. You send it, we run it & store it.

---------
##### Esky
*(noun)* | /**eh**·skee/*ɛ*sˈki/
> An Australian brand of portable coolers. The term "esky" is also commonly used in Australia to generically refer to portable coolers or ice boxes and is part of the Australian vernacular, in place of words like "cooler" or "cooler box" and the New Zealand "chilly bin". The term derives from the word Eskimo.<br>
https://en.wikipedia.org/wiki/Esky

---------

## Huey
https://huey.readthedocs.io/

<b>Start the Consumer</b><br>
In a new terminal, run: `python -m huey.bin.huey_consumer tasks.huey`<br>
This will add all the tasks specificed in `task.py` for the consumer to be able to receive and execute.

## Flask
<b>Start the App</b><br>
In the terminal, run: `python esky.py`<br>
This will serve the app, which you can then post to to run notebooks
e.g.

### Regular Notebook
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"input_notebook": "path/to/repos/esky/esky/notebooks/add.ipynb", "parameters": {"a" : "b"}, "kernel_name": "esky"}' \
  http://localhost:5000/run/
```

### Check tasks and run fake tasks
`curl -X GET 'http://localhost:5000/results/'`

`curl -X GET 'http://localhost:5000/pending/'`

`curl -X GET 'http://localhost:5000/check_task/task_id'`

`curl -X GET 'http://localhost:5000/add_fake_short/'`

`curl -X GET 'http://localhost:5000/add_fake_long/'`