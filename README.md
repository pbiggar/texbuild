This small script continuously builds a LaTeX file in the background and outputs all files into a folder of your choice (default `output/`). Of note is the build file (default `output/build.pdf`) which is what you should open in a pdf viewer of your choice while editing your LaTeX document.

It is less jarring and looks cleaner than what I used to use (`latexmk -pvc`) (The final build file only updates on a successful and complete build. Other build tools will write an incomplete pdf that your pdf viewer can't handle, leading to a broken pdf for a few seconds while you are editing) I also think it's faster, but that might just be the placebo effect.

See [the original stack overflow post](http://stackoverflow.com/questions/1240037/recommended-build-system-for-latex/1394702#1394702) for motivation, usage instruction, and some spicy vim configuration.

Note, this repository is a fork. Changes:

 1. Updated to python3
 2. All output is placed in a folder (default `output/`, modifiable using the config variables at the top of the script)
 3. You can choose the name of the final built pdf (default `output/build.pdf`, modifiable using the config variables at the top of the script)

I highly recommend sioyek as your pdf reader since (unlike zathura, okular, and evince) when it reloads a pdf, it doesn't re-render the entire screen, leading to a much less jarring experience.
