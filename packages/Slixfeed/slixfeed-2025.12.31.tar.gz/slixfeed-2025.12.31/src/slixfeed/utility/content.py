#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class UtilityContent:

    def produce_pdf(content: str, pathname: str):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        """ Produce a PDF document. """
        pathname_pdf = pathname + ".pdf"
        #with open(pathname, "r") as f:
        #    lines = f.readlines()
        lines = content.split("\n")
        x = 5
        y = 800
        line_height = 18
        y_adjustment = 22
        max_width = 570
        page_length = line_height*len(lines) + y_adjustment
        c = canvas.Canvas(pathname_pdf,pagesize=(595, page_length))
        y = page_length-line_height
        for line in lines:
            line = line.rstrip()
            #c.drawString(x, y, line)
            words = line.split(" ")
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if c.stringWidth(test_line, "Helvetica", 12) <= max_width:
                    current_line = test_line
                else:
                    c.drawString(x, y, current_line)
                    y -= 18
                    current_line = word
            y -= line_height
        c.save()
        return pathname_pdf

    def produce_pdf__(content: str, pathname: str):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        """ Produce a PDF document. """
        pathname_pdf = pathname + ".pdf"
        with open(pathname, "r") as f:
            lines = f.readlines()
        x = 5
        y = 800
        max_width = 570
        c = canvas.Canvas(pathname_pdf, pagesize=letter)
        for line in lines:
            line = line.rstrip()
            UtilityContent.draw_wrapped_text(c, line, x, y, max_width)
        c.save()
        return pathname_pdf

    def draw_wrapped_text(c, text, x, y, max_width):
        # Split the text into words
        words = text.split(" ")
        current_line = ""
        
        for word in words:
            # Check if adding the next word exceeds max_width
            test_line = f"{current_line} {word}".strip()
            if c.stringWidth(test_line, "Helvetica", 12) <= max_width:
                current_line = test_line
            else:
                # Draw the current line and reset for the next line
                c.drawString(x, y, current_line)
                y -= 18  # Move down for the next line
                
                # Start a new line with the current word
                current_line = word
                
                # Check if we need to start a new page
                if y < 36:  # If the position is too low on the page
                    c.showPage()
                    y = 800  # Reset y position for a new page
                    
        # Draw any remaining text in the current line
        if current_line:
            c.drawString(x, y, current_line)

    def _produce_pdf(content: str, pathname: str):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        """ Produce a PDF document. """
        pathname_pdf = pathname + ".pdf"
        with open(pathname, "r") as f:
            lines = f.readlines()
        x = 5
        y = 800
        c = canvas.Canvas(pathname_pdf)
        for line in lines:
            line = line.rstrip()
            c.drawString(x, y, line)
            y -= 18
            if y < 36:
                c.showPage()
                y = 800
        c.save()
        return pathname_pdf
