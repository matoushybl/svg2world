# svg2world
Convert svg files to worlds for gazebo. Useful for easy creation of mazes.

```shell
poetry run -m python svg2world PATH_TO_SVG
```

After running, be sure to run xacro on the file to generate the final unrolled world file.

## SVG requirements
* the SVG must contain exactly one ellipse whose center denotes the map origin which will be translated to position `[0, 0]` in the world. It is usually desired that the robot spawns in this position, so there should be free space around this origin.

## Inkscape configuration
* enable snapping (`%`)
* `File->Document properties`
    * set units to px
    * set size to something reasonable (16x16)
    * set scale to `1.0`
    * add grid with `1.0` spacing in both axes
* when using the pen tool, select the appropriate mode of operation: `Create a sequence of straight line segments` or `Create a sequence of paraxial line segments`

## License

```
Copyright (c) 2024 Matous Hybl

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
