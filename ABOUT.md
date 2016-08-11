# About Pyncil
Oy there! So you'd like to learn more *about* this application, *Pyncil*? 
Well, it's really, truly quite exciting...here's how it goes:

One day, I was at home, without Internet (relying on cellular data alone), and I 
decided to start on a new Python project. I asked myself, "what can I make?" And 
I chose Qt, or *PyQt* for Python, a GUI framework that was new to me. I had made a 
text editor in the past using the *wxPython* GUI framework, but it wasn't too advanced, 
other than syntax highlighting and crude color customization. So, I decided to make a 
new editor! 

I know, it wasn't *that* exciting, but that's the story. Anyway, like I said, Pyncil 
is written in Python 3, using the PyQt library. At first, I was just making an editor, 
as a learning project for PyQt; but then the application started to grow, and look *really* 
good (compared to my previous editor, *Pyrite*). I would add todo tasks to my todo list I 
created on Wunderlist, complete them, and add more (this is a common production habit of 
mine). 

The cool thing (which I'm boasting) about Pyncil now, is that you can extend it for other 
languages super easily! Also, the color customization is very simple, and designed in a way 
so that pro designers can make theme files, and users can download them to the themes directory, 
and then just set the theme in the preferences!

Since I am (very) biased towards Python, I wanted the editor to be *primarily* used for 
Python. That's why I created these tools:  
* *tabify* - unify the tabs/spaces according to your preferences (use spaces or tabs), since 
Python cares about whitespace a lot
* *run w/Python 2* - execute a *copy* of the code with Python 2
* *run w/Python 3* - execute a *copy* of the code with Python 3

And the *run w/...* tools allow users to test portability of the code; furthermore, the code is 
ran in a standalone shell, so input is allowed, and the editor isn't blocked. To make things better, 
when you run the code, the shell remains in interactive mode (running "*python -i \<file\>*") 
so you can do some debug stuff at the end if you like--or just play/test! 