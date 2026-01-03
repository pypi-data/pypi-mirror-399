# CCinit
<img width="320" height="100" alt="image" src="https://i.ibb.co/WW5V92kJ/ccinit.png" />
<b> ⚠️ This is still a largely experimental thing. </b> 
## License

MIT License. See [LICENSE](LICENSE).

CCinit is a tool that generates a single `main.c` file based on a `/**/` annotation, at the start of the file, (described in a section below) which might hypothetically include libraries written as URLs or, in shorter form, with an initial `/` in the format described below.
## Important notes

It doesn't yet support global variables and some other stuff like the C preprocessor. Use at your own risk.

Note that libraries need to be converted to this format, so that they can work at all.

Also linters as of right now aren't compatible with this special library format.

The `library` directory contains a library made in such a way. 

After all it will put all that into a `main.c` file, that might be gigantic, but which is really supposed to be easily used through features like CTRL + F and terminal text editor.

## Recommendations  
I also recommend you to use to save frequently, by using Git, so that your work might not be lost.

A tool that can, in a way, making so that the entire code of a package is put within the file `main.c`, so it becomes one file. 

The `library` directory is not really supposed to be really be used as one cohesive library, but is instead as a mere test of the program.

## How to install it
This only works on GNU/Linux as of now or it could be used on Windows with a compatibility layer.

To install CCinit, use this, except you might want to replace the `~` directory with something else.

```bash
cd ~
git clone https://github.com/codemanticism/CCinit.git
cp ~/CCinit/ccinit.py ~/.local/bin/ccinit
```
## How to use
### What to type in the terminal
* `ccinit`: Create a `main.c` file.
* `ccinit main.c`: Reads the `main.c` file and actually does all that heavy lifting for you and everything after `\n/*main*/` remains the same.

### How to format the .c file
<b>Important: Don't use the `#include "LIBRARY"` structure wherein LIBRARY refers to the file which has already been specified through the the system of initial annotations I made for this program.</b>

For all of these substrings seperated by ` ` that start with `/`, it already fills all the stuff in, so that, for example, `/[insert_other_project]/refs/heads/main/main.c` if used in the correct context can make it so that it already fills in the rest, meaning the `https://raw.githubusercontent.com/codemanticism` part, in this case.

It creates a `compile.sh` file, if there's not one and no arguments are specified, which is supposed to compile it with `gcc`.

If there's no `main.c` in the root of the directory, it will create a `main.c` file and no further arguments are provided in the context. If there is one argument, then it will download all the dependencies listed like so, at the start of the file.

An example:
```c
/*https://raw.githubusercontent.com/codemanticism/CCinit/refs/heads/main/libraries/calc.c /random.c*/
//^Where the URLs go.
/*main*/
int main(){
}
...
```
or (it should work):
```c
/*/calc.c /random.c*/
//IF PATH is https://raw.githubusercontent.com/codemanticism/CCinit/refs/heads/main/libraries/something.c 
//^Where the URLs go.
/*main*/
int main(){
}
...
```
It has to be styled like this: `/*example*/`, not like that: `//example`. It has to be the very first line of the file, so the file has to start with `/*`.
## Limits

It was made to be used for `.c` files only. I wanted to make using C easier and more fun to use, so that it could be more like working with `pip`.
