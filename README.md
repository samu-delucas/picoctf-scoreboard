# picoctf-scoreboard
Custom scoreboard for your [picoCTF](https://play.picoctf.org/classrooms/6859) classroom.

![image](https://github.com/samu-delucas/picoctf-scoreboard/assets/55582807/293632a0-ac6b-45b5-a282-7fbd98170df5)

## Why

PicoCTF does not have scoreboards for classrooms. This is a simple web app that fetches the data using the picoCTF API and displays it in a user-friendly way.

It is mainly intended for teachers who want to display the scoreboard on a projector during a session.

## How to run

Clone the repository:
```console
$ git clone https://github.com/samu-delucas/picoctf-scoreboard.git
```

Edit the `config.py` file with your own settings:
```python
# Your classroom ID (int)
# You can find this by going to the classroom page and looking at the URL
# i.e. https://play.picoctf.org/classroom/<your-classroom-id>
CLASSROOM_ID = 0

# Your picotf cookies
# These can be found in your browser's developer tools
COOKIES = {
    'sessionid': 'your-session-id',
    'csrftoken': 'your-csrf-token',
    # 'cf_clearance': '',
    # '__cf_bm': '',
}
```

Finally, run the app:

**Docker**
```console
$ cd picoctf-scoreboard
$ docker build -t picoctf-scoreboard .
$ docker run picoctf-scoreboard
```

**Manual**
```console
$ cd picoctf-scoreboard
$ pip install -r requirements.txt
$ flask --app scoreboard run
```

To delete the saved data and start over, delete the `scoreboard.json` file.

⚠️ **Important**: 
- The app will only work if you have the necessary permissions to access the picoCTF API.
- The Dockerfile runs a development server, which is not suitable for production.
- If you get `Internal Server Error`, it might be because the `challenges.json` file is outdated. Delete it and try again.

## Features
- URL parameters:
    - `?refresh=n` will refresh the scoreboard every `n` seconds.
    - `?demo` will display a demo scoreboard with random data.
- Graph:
    - **Click + Drag**: zoom in.
    - **Mouse wheel**: zoom in/out.
    - **Hover legend**: highlight the line of the hovered player.
    - **Click legend**: hide/show the line of the clicked player.

## TODO
- [ ] Refresh scoreboard without refreshing the page (AJAX)
- [ ] Double-click on graph to reset zoom

## License
This project is available under the [MIT license](https://opensource.org/license/MIT).
