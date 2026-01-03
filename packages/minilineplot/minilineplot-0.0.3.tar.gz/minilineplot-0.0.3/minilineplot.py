
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
    "Defines a Line"
    values:list[tuple]
    color:str
    stroke:int = 3
    label:str = ""


# Note values is a list of x,y tuples, x and y being integers or floats.

# If the Axis 'xstrings' argument is set as strings along the x axis,
# for example months of the year, then values tuples should have
# x values as a percentage along the x axis (from 0 to 100).

# Similarly if the Axis 'ystrings' argument is set as strings up
# the y axis, then values tuples should have y values as percentages.

# Otherwise x,y values should be numeric values between the min and max
# Axis attributes

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
                                                       # If any strings are set here, the following x axis arguments are ignored, and line
                                                       # x values should all be percentages between 0 and 100.

    #### or if xstrings is empty, the following will define the x axis ####

    xformat:str = ".2f"            # How the x axis numbers are formatted,
    xmin:float|int = 0             # minimum x value
    xmax:float|int = 10            # maximum x value
    xintervals:int = 5             # interval spacing of values along the x axis, 5 would be five intervals and six values.

    ystrings:list[str] = field(default_factory=list)   # A list of strings used as the y axis values. If any strings are
                                                       # set here, the following y axis arguments are ignored, and line
                                                       # y values should all be percentages between 0 and 100.

    #### or if ystrings is empty, the following will define the y axis ####

    yformat:str = ".2f"            # How the y axis numbers are formatted,
    ymin:float|int = 0             # minimum y value
    ymax:float|int = 10            # maximum y value
    yintervals:int = 5             # interval spacing of values up the y axis, 5 would be five intervals and six values.

    # xformat and yformat is a format string describing how numbers are printed
    # for example the string ".2f"   gives a number to two decimal places

    title:str = ""                 # printed at the top of the chart
    description:str = ""           # printed at the bottom of the chart

    verticalgrid:int = 1           # 0 is no vertical grid lines, 1 is a line for every x axis interval, 2 is a line for every second interval.
    horzontalgrid:int = 1          # 0 is no horizontal grid lines, 1 is a line for every y axis interval, 2 is a line for every second interval.

    # The following colors are SVG colors, using standard strings

    gridcol:str="grey"             # Color of the chart grid
    axiscol:str="black"            # Color of axis, title and description
    chartbackcol:str="white"       # the background colour of the chart
    backcol:str="white"            # The background colour of the whole image


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


    def _validate(self):
        "Some minimal validation of input values"
        if self.xstrings:
            # all x values should be between 0 and 100
            for line in self.lines:
                for point in line.values:
                    if point[0] < 0 or point[0] > 100:
                        raise ValueError("x values should be between 0 and 100")
        else:
            if self.xmax <= self.xmin:
                raise ValueError("xmax, xmin values incorrect")
            for line in self.lines:
                for point in line.values:
                    if point[0] < self.xmin or point[0] > self.xmax:
                        raise ValueError("x value exceeds limits")

        if self.ystrings:
            # all y values should be between 0 and 100
            for line in self.lines:
                for point in line.values:
                    if point[1] < 0 or point[1] > 100:
                        raise ValueError("y values should be between 0 and 100")
        else:
            if self.ymax <= self.ymin:
                raise ValueError("ymax, ymin values incorrect")
            for line in self.lines:
                for point in line.values:
                    if point[1] < self.ymin or point[1] > self.ymax:
                        raise ValueError("y value exceeds limits")


    def _render(self) -> ET.Element:
        "Render the svg image as an elementTree element"

        # some limited validation
        self._validate()          

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
        if self.ystrings:
            ytextlen = max( len(ystring) for ystring in self.ystrings )
        else:
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

        ## optimize chart width, so intervals fall on integer pixels

        # to get best width of chart, xintervals = number of intervals on the x axis
        if self.xstrings:
            xintervals = len(self.xstrings) - 1
        else:
            xintervals = self.xintervals

        if self.ystrings:
            yintervals = len(self.ystrings) - 1
        else:
            yintervals = self.yintervals

        # get better sizing of chart, so interval measurements are all in integers
        xintervalwidth = round(chartwidth / xintervals)
        chartwidth = xintervalwidth * xintervals
        rightspace = self.imagewidth - leftspace - chartwidth

        # to get height of chart
        yintervalwidth = round(chartheight / yintervals)
        chartheight = yintervalwidth * yintervals
        botspace = self.imageheight - topspace - chartheight
        
        ### rectangle of chart background color
        ET.SubElement(doc, 'rect', {"width":str(chartwidth), "height":str(chartheight),
                                    "x":str(leftspace), "y":str(topspace), "fill":self.chartbackcol})

        # title at top of chart
        if self.title:
            t = ET.SubElement(doc, 'text', {"x":str(leftspace + chartwidth//4), "y":str(10 + self.fontsize),
                                            "fill":self.axiscol})
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
        for tick in range(yintervals+1):
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
            for hline in range(yintervals):
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
                                                  "fill":self.axiscol})
                tel.text = txt
                xpos += xintervalwidth
        else:
            xvalinterval = (self.xmax - self.xmin) / xintervals
            xval = self.xmin
            xsetformat = '{:' + self.xformat + '}'
            for interval in range(xintervals+1):
                tel = ET.SubElement(doc, 'text', {"x":str(xpos), "y":str(ypos),
                                                  "fill":self.axiscol})
                tel.text = xsetformat.format(xval)
                xpos += xintervalwidth
                xval += xvalinterval

        # description at bottom of chart
        if self.description:
            desc = ET.SubElement(doc, 'text', {"x":str(leftspace), "y":str(self.imageheight - 10 - self.fontsize),
                                              "fill":self.axiscol})
            desc.text = self.description

        # y axis text
        ypos = topspace + self.fontsize//5
        if self.ystrings:
            for txt in reversed(self.ystrings):
                tel = ET.SubElement(doc, 'text', {"x":str(leftspace-10), "y":str(ypos),
                                                  "fill":self.axiscol, "text-anchor":"end"})
                tel.text = txt
                ypos += yintervalwidth
        else:
            yvalinterval = (self.ymax - self.ymin) / yintervals
            yval = self.ymax
            for interval in range(yintervals+1):
                tel = ET.SubElement(doc, 'text', {"x":str(leftspace-10), "y":str(ypos),
                                                  "fill":self.axiscol, "text-anchor":"end"})
                tel.text = ysetformat.format(yval)
                ypos += yintervalwidth
                yval -= yvalinterval

        # draw the lines
        for line in self.lines:
            points = []
            for x,y in line.values:
                if self.ystrings:
                    # y values as percentage of chartheight
                    py = round(topspace+chartheight - y*chartheight/100)
                else:
                    py = round(topspace+chartheight - (y-self.ymin)*chartheight/(self.ymax-self.ymin))
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

