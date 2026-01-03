
# minilineplot.py is a single module producing an SVG image of a chart with one or more plotted lines.
#
# Intended to be as simple as possible, with no dependencies.
#
# The chart has a left vertical axis and a bottom horizontal axis, grid lines are possible,
#
# Two classes are defined.
#
# Line, containg x,y points which creates a line to be plotted 
#
# Axis which creates the axis, and to which Line objects can be added.
#
# The Axis class has methods to create an svg string suitable for embedding in an html document
# it can also create an svg image, either as a bytes object, or saved to a file.


from dataclasses import dataclass, field
import xml.etree.ElementTree as ET


@dataclass
class Line:
    "Defining a Line"
    values:list[tuple]
    color:str
    stroke:int = 3
    label:str = ""


# Note values is a list of x,y tuples

# If the Axis 'xstrings' argument is set as strings along the x axis,
# for example months of the year, then the Line values tuples should be:
# x is a percentage along the x axis, y is the actual value.
# so [(0,59), (100,28)]  is a line from the extreme left (0%) value 59
#                                     to the extreme right (100%) value 28

# If the Axis x axis is defined as numbers rather than strings
# then each (x,y) tuple should be the numeric values to be plotted.


# color is an SVG color, using standard strings such as

# Color Names: "red", "blue" etc.
# Hex Codes: "#FF0000" for red.
# RGB/RGBA: "rgb(255,0,0)" or "rgba(255,0,0,0.5)" (with opacity).
# HSL/HSLA: "hsl(0,100%,50%)" or "hsla(0,100%,50%,0.5)" (hue, saturation, lightness, alpha)

# stroke is the width of the plotted line in SVG drawing units, 1 for a thin line
# label is a text label used in a key, if not given, the key will not be drawn



@dataclass
class Axis:
    "Defines the axis of the chart"

    lines:list[Line] = field(default_factory=list)       # list of Line objects

    fontsize:int = 24
    imagewidth:int = 800
    imageheight:int = 600

    xstrings:list[str] = field(default_factory=list)   # A list of strings used as the x axis values, use for text values such as months, etc.,
                                                       # If any strings are set here, the following xaxis numbers are ignored

    #### or use numbers for the x axis ####

    xformat:str = ".2f"            # How the x axis numbers are formatted,
    xmin:float|int = 0             # minimum x value
    xmax:float|int = 10            # maximum x value
    xintervals:int = 5             # interval spacing of values along the x axis, 5 would be five intervals and six values.

    # The y axis is always just numbers

    yformat:str = ".2f"            # How the y axis numbers are formatted,
    ymin:float|int = 0             # minimum y value
    ymax:float|int = 10            # maximum y value
    yintervals:int = 5             # interval spacing of values up the y axis, 5 would be five intervals and six values.


    title:str = ""                 # printed at the top of the chart
    description:str = ""           # printed at the bottom of the chart

    verticalgrid:int = 1           # 0 is no vertical grid lines, 1 is a line for every x axis interval, 2 is a line for every second interval.
    horzontalgrid:int = 1          # 0 is no horizontal grid lines, 1 is a line for every y axis interval, 2 is a line for every second interval.

    # The following colors are SVG colors, using standard strings

    gridcol:str="grey"             # Color of the chart grid
    axiscol:str="black"            # Color of axis, title and description
    chartbackcol:str="white"       # the background colour of the chart
    backcol:str="white"            # The background colour of the whole image


    # xformat and yformat is a format string describing how numbers are printed
    # for example the string ".2f"   gives a number to two decimal places


    def to_string(self, xml_declaration:bool = False) -> str:
        """Return a string SVG object. If xml_declaration is True,
           an xml tag will be included in the returned string which
           is usually required when creating an svg image file but not
           required if embedding the code directly into an html document"""
        doc = self._render()
        return ET.tostring(doc, encoding="unicode", xml_declaration=xml_declaration)

    def to_bytes(self, xml_declaration:bool = True) -> bytes:
        """Return a bytes SVG object. If xml_declaration is True,
           an xml tag will be included in the returned bytes which
           is usually required when creating an svg image file but not
           required if embedding the code directly into an html document"""
        doc = self._render()
        return ET.tostring(doc, xml_declaration=xml_declaration)

    def to_file(self, filepath:str) -> None:
        "Save the plot to an svg image file"
        tree = ET.ElementTree(self._render())
        tree.write(filepath, xml_declaration=True)

    def _render(self) -> ET.Element:
        "Render the svg image as an elementTree element"

        # get the spacing around the chart

        if self.title:
            topspace = self.fontsize * 3  # space at top for title
        else:
            topspace = self.fontsize * 2

        if self.description:
            botspace = self.fontsize * 5  # space at bottom for description
        else:
            botspace = self.fontsize * 3

        # initial chartheight
        chartheight = self.imageheight - topspace - botspace

        # get length of the yaxis text which will be on the left side of the chart
        ysetformat = '{:' + self.yformat + '}'
        ytextlen = max( len(ysetformat.format(self.ymin)), len(ysetformat.format(self.ymax)))

        # define width leftspace which will be to the left of the chart
        leftspace =  self.fontsize * ytextlen

        # define width rightspace which will be to the right of the chart, this will contain
        # line keys, if line labels have been defined
        labelengths = tuple(len(line.label) for line in self.lines)
        if labelengths:
            # if labels, increase rightspace to give space for an index
            longest = max(labelengths)
            rightspace = max(self.imagewidth // 10, self.fontsize * (6 + longest)//2)
        else: 
            rightspace =  self.imagewidth // 10

        # initial chartwidth
        chartwidth = self.imagewidth - leftspace - rightspace

        # Start the document
        doc = ET.Element('svg', width=str(self.imagewidth), height=str(self.imageheight), version='1.1', xmlns='http://www.w3.org/2000/svg')
        textstyle = ET.SubElement(doc, 'style')
        textstyle.text = f"""text {{
      font-family: Arial, Helvetica, sans-serif;
      font-size: {self.fontsize}px;
      font-weight: Thin;
    }}
"""

        ### rectangle of background colour, the same size as the whole image
        ET.SubElement(doc, 'rect', {"width":str(self.imagewidth), "height":str(self.imageheight), "x":"0","y":"0", "fill":self.backcol})

        ### rectangle of chart background color
        # to get best width of chart, xintervals = number of intervals on the x axis
        if self.xstrings:
            xintervals = len(self.xstrings) - 1
        else:
            xintervals = self.xintervals

        # get better sizing of chart, so interval measurements are all in integers
        xintervalwidth = round(chartwidth / xintervals)
        chartwidth = xintervalwidth * xintervals
        rightspace = self.imagewidth - leftspace - chartwidth

        # to get height of chart, self.yintervals = number of intervals on the y axis
        yintervalwidth = round(chartheight / self.yintervals)
        chartheight = yintervalwidth * self.yintervals
        botspace = self.imageheight - topspace - chartheight
        

        ET.SubElement(doc, 'rect', {"width":str(chartwidth), "height":str(chartheight),
                                    "x":str(leftspace), "y":str(topspace), "fill":self.chartbackcol})

        # title at top of chart
        if self.title:
            t = ET.SubElement(doc, 'text', {"x":str(leftspace + chartwidth//4), "y":str(10 + self.fontsize),
                                            "fill":self.axiscol, "fill":self.axiscol})
            t.text = self.title

        ### x axis
        ET.SubElement(doc, 'line', {"x1":str(leftspace-1), "y1":str(topspace+chartheight),
                                    # note x1 has minus 1 as the stroke is 3, so this covers the corner
                                    "x2":str(leftspace+chartwidth), "y2":str(topspace+chartheight),
                                    "style":f"stroke:{self.axiscol};stroke-width:3"} )
        # add x ticks
        xpos = leftspace
        for tick in range(xintervals+1):
            ET.SubElement(doc, 'line', {"x1":str(xpos), "y1":str(topspace+chartheight-3), 
                                        "x2":str(xpos), "y2":str(topspace+chartheight+6), "style":f"stroke:{self.axiscol};stroke-width:1"} )
            xpos += xintervalwidth


        ### y axis
        ET.SubElement(doc, 'line', {"x1":str(leftspace), "y1":str(topspace),
                                    "x2":str(leftspace), "y2":str(topspace+chartheight+1),
                                                              # note y2 has plus 1 as the stroke is 3, so this covers the corner
                                    "style":f"stroke:{self.axiscol};stroke-width:3"} )
        # add y ticks
        ypos = topspace
        for tick in range(self.yintervals+1):
            ET.SubElement(doc, 'line', {"x1":str(leftspace-6), "y1":str(ypos),
                                        "x2":str(leftspace+3), "y2":str(ypos), "style":f"stroke:{self.axiscol};stroke-width:1"} )
            ypos += yintervalwidth

        # vertical grid lines
        if self.verticalgrid:
            xpos = leftspace
            increment = xintervalwidth * self.verticalgrid
            for vline in range(xintervals):
                xpos += increment
                if xpos > leftspace+chartwidth:
                    break
                ET.SubElement(doc, 'line', {"x1":str(xpos), "y1":str(topspace),
                                            "x2":str(xpos), "y2":str(topspace+chartheight-1),
                                            "style":f"stroke:{self.gridcol};stroke-width:1"} )

        # horizontal grid lines
        if self.horzontalgrid:
            ypos = topspace+chartheight
            decrement = yintervalwidth * self.horzontalgrid
            for hline in range(self.yintervals):
                ypos -= decrement
                if ypos < topspace:
                    break
                ET.SubElement(doc, 'line', {"x1":str(leftspace+1), "y1":str(ypos),
                                            "x2":str(leftspace+chartwidth), "y2":str(ypos),
                                            "style":f"stroke:{self.gridcol};stroke-width:1"} )

        # x axis text
        xpos = leftspace - (self.fontsize//2)
        ypos = topspace+chartheight + 10 + self.fontsize

        if self.xstrings:
            for txt in self.xstrings:
                tel = ET.SubElement(doc, 'text', {"x":str(xpos), "y":str(ypos),
                                                  "fill":self.axiscol, "fill":self.axiscol})
                tel.text = txt
                xpos += xintervalwidth
        else:
            xvalinterval = (self.xmax - self.xmin) / xintervals
            xval = self.xmin
            xsetformat = '{:' + self.xformat + '}'
            for interval in range(xintervals+1):
                tel = ET.SubElement(doc, 'text', {"x":str(xpos), "y":str(ypos),
                                                  "fill":self.axiscol, "fill":self.axiscol})
                tel.text = xsetformat.format(xval)
                xpos += xintervalwidth
                xval += xvalinterval

        # description at bottom of chart
        if self.description:
            desc = ET.SubElement(doc, 'text', {"x":str(leftspace), "y":str(self.imageheight - 10 - self.fontsize),
                                              "fill":self.axiscol, "fill":self.axiscol})
            desc.text = self.description

        # y axis text
        yvalinterval = (self.ymax - self.ymin) / self.yintervals
        yval = self.ymax
        ypos = topspace + self.fontsize//5
        for interval in range(self.yintervals+1):
            tel = ET.SubElement(doc, 'text', {"x":str(leftspace-10), "y":str(ypos),
                                              "fill":self.axiscol, "fill":self.axiscol, "text-anchor":"end"})
            tel.text = ysetformat.format(yval)
            ypos += yintervalwidth
            yval -= yvalinterval

        # draw the lines
        yspan = self.ymax-self.ymin
        for line in self.lines:
            points = []
            for x,y in line.values:
                py = round(topspace+chartheight - (y-self.ymin)*chartheight/yspan)
                if self.xstrings:
                    # x values as percentage of chartwidth
                    px = round(leftspace + x*chartwidth/100)
                else:
                    px = round(leftspace + (x-self.xmin)*chartwidth/(self.xmax-self.xmin))
                points.append(f"{px},{py}")
            pointstring = " ".join(points)
            ET.SubElement(doc, 'polyline', {"style":f"fill:none;stroke:{line.color};stroke-width:{line.stroke}", "points":pointstring})


        # draw the index
        if labelengths:
            # get lines in order of the last point y value
            sortedlines = sorted(self.lines, key = lambda x:x.values[-1][1], reverse=True)
            ypos = topspace
            xpos = self.imagewidth - rightspace + self.fontsize + self.fontsize
            for line in sortedlines:
                lbl = ET.SubElement(doc, 'text', {"x":str(xpos),
                                                  "y":str(ypos),
                                                  "fill":line.color,
                                                  "font-weight":"Thin"})

                lbl.text = line.label
                ypos += 3*self.fontsize


        return doc
       


if __name__ == "__main__":

    # Example plot

    line1 = Line(values = [(0,15), (2,20), (4, 50), (6, 75), (10, 60)],
                color = "green",
                label = "green line")

    line2 = Line(values = [(0,95), (2,80), (5, 60), (7, 55), (8, 35), (9, 25), (10, 10)],
                color = "blue",
                label = "blue line")

    line3 = Line(values = list((x,x**2) for x in range(11)),
                color = "red",
                stroke = 3,
                label = "y = x squared")


    example = Axis( [line1, line2, line3],
                    xformat = ".0f",  
                    xmin = 0,
                    xmax = 10,
                    xintervals = 10,
                    ymin = 0,
                    ymax = 100,
                    yintervals = 5,     
                    title = "Example Chart",
                    description = "Fig 1 : Example chart",
                  )

    # If chart text starts overlapping, either decrease font size,
    # or increase the image size while keeping fontsize the same

    print("Creating file test.svg")
    example.to_file("test.svg")
    print("Done")

