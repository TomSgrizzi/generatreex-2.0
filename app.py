from flask import Flask, request, render_template, session, redirect, url_for, flash, send_file, jsonify, abort, make_response, send_from_directory
import matplotlib.pyplot as plt
import os
import fitz
import shutil
from datetime import datetime
from pdf2image import convert_from_path
import subprocess
import re
from user_agents import parse
from PIL import Image

app = Flask(__name__)  # Make sure to use __name__ instead of name

# You need to set a secret key to use sessions
app.secret_key = os.environ.get('SECRET_KEY', 'default_key')
app.config['DEBUG'] = True

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    ua = parse(user_agent)
    if ua.is_mobile:
        return render_template('index-mobile.html')
    else:
        return render_template('index.html')
    

@app.route('/submit', methods=['POST'])
def submit():
    output_png_path = os.path.join(app.static_folder, 'download\css\output-1.png')
    output_png_mobile_path =os.path.join(app.static_folder, 'download-mobile\css\output-1.png')

    # Check if the file exists and delete it
    if os.path.exists(output_png_path):
        os.remove(output_png_path)
        print("Pre-existent PNG removed")
    else:
        print("No pre-existing PNG file found")

    # Retrieve the value of "structure" from the submitted form
    structure = request.form.get('structure')
    movement = int(request.form.get('movement_lines'))
    from_nodes = request.form.get('from_nodes')
    to_nodes = request.form.get('to_nodes')
    direction_out = request.form.get('direction_out')
    direction_in = request.form.get('direction_in')

    
    #Input filtering
    if not structure:  # Check if structure is empty or None
        print("""
              ERROR: No structure input provided
              """)
        flash("Please, enter a structure before submitting", "error_empty_structure")
        return redirect(url_for('index'))  # Assuming 'index' is the endpoint for the page with the form
    
    if not structure.startswith("["):
        print("""
            ERROR: The structure doesn't start with [!
            """)
        flash("Your structure must begin with '['", "error_squared_beginning")
        return redirect(url_for('index')) 

    # Counting the occurrences of '[' and ']'
    user_input = structure #converting the values for easiness of updating the app
    session['user_input'] = user_input
    print("User input stored in session:", session['user_input']) 

    count_open_brackets = user_input.count('[')
    count_close_brackets = user_input.count(']')

    # I'm checking if the counts are equal
    if count_open_brackets != count_close_brackets:
        print("""
            ERROR: Uneven number of opening and closing brackets!
            """)
        flash('Invalid bracketing in the input. Check your structure.', 'error_bracketing')
        return redirect(url_for('index')) 

    # Movement filtering
    
    input_nodes = from_nodes.split(',')
    output_nodes = to_nodes.split(',')

    if movement > 0:
        if len(output_nodes) != len(input_nodes):
            print("""
            ERROR: The number of goals and probes don't match!
            """)
            flash("The number of goals and probes don't match!", 'error_probe_goal_count')
            return redirect(url_for('index')) 
        elif len(output_nodes) != movement:
            print("""
            ERROR: The number of goals is different from the number of movement lines!
            """)
            flash("The number of goals is different from the number of movement lines!", 'error_goal_count')
            return redirect(url_for('index')) 
        elif len(input_nodes) != movement:
            print("""
            ERROR: The number of probes is different from the number of movement lines!
            """)
            flash("The number of probes is different from the number of movement lines!", 'error_probe_count')
            return redirect(url_for('index')) 
        
    output_directions = direction_out.split(',')    
    input_directions = direction_in.split(',')

    if movement > 0:
        if len(output_directions) != len(input_directions):
            output_directions = []
            input_directions = []
            print("Output direction is erased because directions don't match: " + str(output_directions) + str(input_directions))
        elif len(output_directions) != movement:
            output_directions = []
            input_directions = []
            print("Output direction is erased because directions don't match: " + str(output_directions) + str(input_directions))
        elif len(input_directions) != movement:
            input_directions = []
            output_directions = []
            print("Input direction is erased because directions don't match: " + str(input_directions) + str(output_directions))
            


    #Turning the labels of probes and goals into a list of input and output
    node_pairs = []
    for i in range(len(output_nodes)):
        pair = ""
        pair += input_nodes[i]
        pair += ", "+output_nodes[i]
        node_pairs.append(pair)

    #Turning the directions of the lines into a list of input and output
    direction_pairs = []

    if direction_in and direction_out:
        for i in range(len(output_directions)):
            pair = ""
            pair += input_directions[i]
            pair += ", "+output_directions[i]
            direction_pairs.append(pair)


    #Debug prints
    print(" ")
    print("---------------USER'S INPUT---------------")
    print(" ")
    print("The structure submitted is: " + user_input)
    print("The number of movements required is: " + str(movement))  
    print("The labels of the goals are: " + from_nodes)
    print("The labels of the probes are: " + to_nodes)
    print("The directions from the goals are: " + direction_out)
    print("The directions to the probes are: " + direction_in)
    print("---------------PREPROCESSED INPUT---------------")
    print("The node pairs are the following: " + str(node_pairs))
    print("The direction pairs are the following: " + str(direction_pairs))
    print(" ")

    ### Now let's do the actual work

    # No-movement tracks
    if movement == 0:
        print("--------------------- STARTING NO MOVEMENT TRACK---------------------")
        # Introducing the tree template
        latex_template = r'''
        \documentclass{standalone}
        \usepackage{tikz}
        \usepackage{forest}

        \begin{document}
        \begin{forest}
            for tree={calign=fixed edge angles},
            {user_input}
        \end{forest}
        \end{document}
        '''

        latex_document = latex_template.replace("{user_input}", user_input)
        print("Latex document:", latex_document)  # Debug print
        session['latex_document'] = latex_document

        # Writing the LaTeX code to a file
        with open("document.tex", "w") as file:
            file.write(latex_document)

        try:
            # Running pdflatex with a timeout to avoid hanging
            result = subprocess.run(["pdflatex", "document.tex"], timeout=30, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # If the return code indicates an error, handle it
            if result.returncode != 0:
                print("pdflatex failed with return code:", result.returncode)
                print("Standard Output:", result.stdout.decode())
                print("Standard Error:", result.stderr.decode())
                raise subprocess.CalledProcessError(result.returncode, "pdflatex")
        except subprocess.CalledProcessError as e:
            print("An error occurred while generating the PDF:", e)
            flash("PDF generation failed. Please check your input for invalid characters. See the guide for more information.", "error_pdf_generation")
            return redirect(url_for('index'))  # Replace 'index' with your main page's route
        except subprocess.TimeoutExpired as e:
            print("The pdflatex command timed out:", e)
            flash("PDF generation timed out. Please check your input for invalid characters. See the guide for more information.", "error_timeout")  # Flash the error message
            return redirect(url_for('index'))  # Replace 'index' with your main page's route
        
        session['latex_document'] = latex_document
        def pdf_to_transparent_image(pdf_path, output_path, page_number=0, zoom_factor=2.0):
            # Open the PDF file
            pdf_document = fitz.open(pdf_path)
            
            # Select the page
            page = pdf_document.load_page(page_number)
            
            # Define the zoom matrix
            zoom_matrix = fitz.Matrix(zoom_factor, zoom_factor)
            
            # Convert the page to a pixmap with the specified zoom factor
            pix = page.get_pixmap(matrix=zoom_matrix)
            
            # Convert pixmap to an image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to RGBA
            img = img.convert("RGBA")
            
            # Make the white background transparent
            datas = img.getdata()
            new_data = []
            
            for item in datas:
                # Change all white (also shades of whites)
                # to transparent
                if item[:3] == (255, 255, 255):
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            
            img.putdata(new_data)
            
            # Save the image
            img.save(output_path, "PNG")


        # Check if the PDF was created successfully
        if os.path.exists("document.pdf"):
            print("PDF successfully created.")
                                   
           
            # Example usage:
            pdf_path = 'document.pdf'
            output_path = 'static/download/css/output-1.png'
            pdf_to_transparent_image(pdf_path, output_path, zoom_factor=4.0)  # Increase the zoom factor to increase resolution

            with Image.open(output_path) as img:
                width, height = img.size


            print(f"PNG Width before resizing: {width}, Height: {height}")

            highest_value_size = []
        
            if width>height:
                highest_value_size.append("width")
                highest_value_size.append(width)
            else:
                highest_value_size.append("height")
                highest_value_size.append(height)
            
            print("The higher value is: "+ str(highest_value_size))

            ua = session.get('ua')
            def resize_image(input_path, output_path, fixed_width=418, fixed_height=383):
                # Open the image
               
                img = Image.open(input_path)
                width, height = img.size

                # Determine the highest dimension
                
                scale_factor = fixed_height / float(height)
                new_width = int(width * scale_factor)
                new_height = fixed_height

                # Resize the image
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Save the resized image
                resized_img.save(output_path)

            # Example usage:
            resize_image(output_path, output_path)
            with Image.open(output_path) as img:
                width, height = img.size

            print(f"PNG Width after resizing: {width}, Height: {height}")

            source_file = os.path.join(app.root_path, 'static\download\css', 'output-1.png')
    
            # Define the destination directory
            destination_folder = os.path.join(app.root_path, 'static\download-mobile\css')
            
            # Ensure the destination folder exists
            if not os.path.exists(destination_folder):
                print("destination does not exists")
            
            # Define the destination file path
            destination_file = os.path.join(destination_folder, 'output-1.png')
            
            shutil.copy2(source_file, destination_file)
            
            return redirect(url_for('download'))
        else:
            print("PDF generation failed.")
            # Handle the error appropriately
            flash("PDF generation failed.", "error_pdf_generation")
            return redirect(url_for('index'))

    if movement != 0:
        print("""
              --------------------- STARTING MOVEMENT TRACK---------------------
              """)

        print('The tree structure is: ' + user_input)
        print("The pairs of nodes are: ", node_pairs)  # Debug print

        latex_template = r'''
        \documentclass{standalone}
        \usepackage{tikz}
        \usepackage{amsmath}
        \usepackage{forest}

        \begin{document}
        \begin{forest}
            for tree={calign=fixed edge angles},
            {user_input}
            {movement_strings}
        \end{forest}
        \end{document}
        '''
        # What follows is a cumbersone solution to the proper formatting of bar nodes. L'importante è che funzioni
        # Using a regular expression to match words that may end with an apostrophe
        pattern = re.compile(r"(\b\w+'?\b)")

        # Defining a function that adds ",name=element" to each element
        def add_name_attr(match):
            element = match.group(1)  # The matched element including an apostrophe if present
            return f"{element},name={element}"

        # Replacing elements in user_input using the add_name_attr function
        output_tree = pattern.sub(add_name_attr, user_input)

        # Regular expression to match the patterns where the element after "=" is followed by an apostrophe
        pattern = re.compile(r"(\w+)(,name=\w+')" )

        # Function to add an apostrophe before the comma if the element after "=" is followed by an apostrophe
        def add_apostrophe_before_comma(match):
            return f"{match.group(1)}',name={match.group(2)[5:]}"

        # Replace the matched patterns in the string using the add_apostrophe_before_comma function
        modified_string = pattern.sub(add_apostrophe_before_comma, output_tree)
        corrected_string = re.sub(r"name=+", "name=", modified_string)
        print("The processed tree structure is: " + corrected_string)

        ################  ISOLATING EACH CASES #######################

        def extract_words(sentence):
            words = []
            current_word = ''

            inside_brackets = False
            for char in sentence:
                if char == '[':
                    inside_brackets = True
                    if current_word:
                        words.append(current_word)
                        current_word = ''
                elif char == ']':
                    inside_brackets = False
                    if current_word:
                        words.append(current_word)
                        current_word = ''
                elif char == ' ' and not inside_brackets:
                    if current_word:
                        words.append(current_word)
                        current_word = ''
                else:
                    current_word += char

            if current_word:
                words.append(current_word)

            return words

        content_with_multiple_names = extract_words(corrected_string)
        print(content_with_multiple_names)
        # Example output for future references: ["T',name=T' ", 'il,name=il Giulio,name=Giulio ', 'mangia,name=mangia ', 'la,name=la mela,name=mela bruna,name=bruna']


        ######## TENIAMO SOLO GLI ELEMENTI CHE SONO PROBLEMATICI #########

        def filter_elements_with_multiple_names(lst):
            filtered_list = []
            for item in lst:
                if item.count("name") > 1:
                    filtered_list.append(item)
            return filtered_list

        # Applying the function
        filtered_result = filter_elements_with_multiple_names(content_with_multiple_names)
        print(str(filtered_result) + " filtered result checkpoint")
        # Example output for f. references: ['il,name=il Giulio,name=Giulio ', 'la,name=la mela,name=mela bruna,name=bruna']


        ######## HANDLING OF SPACES ################
        if filtered_result:
            def store_words_before_comma(input_string):
                words = ""
                word_list = []
                for char in input_string:
                    if char == ',':
                        if words:  # Add the accumulated words before the comma to the list
                            word_list.append(words.strip())
                        words = ""
                    else:
                        words += char
                if words:  # It appends the last word if there's no comma at the end
                    word_list.append(words.strip())

                # Reconstruct the sentence from the filtered words. We are almost there
                result = ' '.join(word_list)

                equal_words = result.split()

                filtered_words = [word for word in equal_words if "=" not in word]

                output = ' '.join(filtered_words)
                return output

            def substitute_word(text, old_word, new_word):
                return text.replace(old_word, new_word)

            print(""" 
                    The benchmark is  """ + str(filtered_result))

            for i in filtered_result:

                corrected_label = store_words_before_comma(i)
                print(corrected_label + " was: " + i)

                new_label = corrected_label+",name="+corrected_label
                print("""
                        new label is """ + new_label)
                new_output = substitute_word(corrected_string, i, new_label)
                corrected_string = new_output
                print("Now the string is " + new_output)

            corrected_string = new_output #halleluja

        print("The pairs of nodes are: ", node_pairs) 
        #####cut here#####
        def count_brackets_between_words(tree_string, start_substring, end_substring):
            start_index = tree_string.find("["+start_substring)
            end_index = tree_string.find("["+end_substring)
            
            # It's important that both substrings are found and start_substring comes before end_substring
            if start_index == -1 or end_index == -1 or start_index >= end_index:
                start_index = tree_string.find(end_substring)
                end_index = tree_string.find(start_substring)
                # Extracting the section of the string between the two substrings
                section = tree_string[start_index:end_index]
            
                # Counting the number of "]" in the section
                count = section.count(']')
            
                return count
            
            # Extracting the section of the string between the two substrings
            section = tree_string[start_index:end_index]
            
            # Counting the number of "]" in the section
            count = section.count(']')
            
            return count

        benchmark_for_extra_nodes = {}  #to be used below

        for pair in node_pairs:
            word1 = [pair.split(',')[0].strip()]
            word2 = [pair.split(',')[1].strip()]
            cleaned_word1 = word1[0].replace("['", "").replace("']", "")
            cleaned_word2 = word2[0].replace("['", "").replace("']", "")
            print(cleaned_word1)
            print(cleaned_word2)
            bracket_count = count_brackets_between_words(corrected_string, cleaned_word1, cleaned_word2)
            benchmark_for_extra_nodes[pair]=bracket_count
            print("Number of ']' characters between '['{}' and '['{}' is: {}".format(cleaned_word1, cleaned_word2, bracket_count))

        print(benchmark_for_extra_nodes)

        eccedenze_dictionary = {}
        normal_lines_dictionary = {}
        for key, value in benchmark_for_extra_nodes.items():
            if value > 2:
                eccedenze_dictionary[key]=value
            else:
                normal_lines_dictionary[key]=value

        print(eccedenze_dictionary)
        print(normal_lines_dictionary)

        tikz_string_template = r"\draw[->,dotted] ({source}) to[out=south west,in=south west] ({goal});"
        tikz_code = []
        print("Len direction pairs is: " + str(len(direction_pairs)))
        if not direction_pairs:
            print("---------------LINE DIRECTIONS NOT DEFINED---------------")
            # Dissecting the tikz line because python interprets curly brackets even when they are not used and it crashes
            scope_tikz_1 = r"\begin{scope}[every node/.style={circle}] \path"
            scope_tikz_2 = r"({source}) coordinate"
            scope_tikz_3 = r"({coordinate_in_the_tree}); \node" 
            scope_tikz_4 = r"[label=above:{}]"
            scope_tikz_5 = r" at ({source})"
            scope_tikz_6 = r"{}; \end{scope}"

            coordinate_tikz = r"\coordinate ({coordinatetopivot}) at ([xshift={xcoord}cm,yshift={ycoord}cm]{coordinata_in_the_tree});"

            extra_tikz = r"\draw[->,dotted] ({source}) to[out=south,in=east]({coordinatetopivot}) to[out=west,in=west]({goal});"

            print(eccedenze_dictionary)
            def assembling_modulating_formula(dic):
                for key, value in eccedenze_dictionary.items():
                    print(value)
                    xcoord = -(float(value)/5+1) #these two are weights that must be tuned with experience, who knows
                    ycoord = -(float(value)/5+1)
                    print(xcoord)
                    print(ycoord)
                    nodes = key.split(',')
                    source = nodes[0].strip()
                    goal = nodes[1].strip()
                    coord_name = "extra"+source
                    coordinate_to_pivot = "pivot"+source
                    specific_scope_2 = scope_tikz_2.format(source=source)
                    specific_scope_tikz_3 = scope_tikz_3.format(coordinate_in_the_tree=coord_name,source=source)
                    specific_scope_tikz_5 =scope_tikz_5.format(source=source)
                    total_tikz_scope = scope_tikz_1 + specific_scope_2 + specific_scope_tikz_3 + scope_tikz_4 +specific_scope_tikz_5 +scope_tikz_6
                    coordinates = coordinate_tikz.format(coordinatetopivot=coordinate_to_pivot, xcoord=xcoord,ycoord=ycoord,coordinata_in_the_tree=coord_name)
                    print(coordinates)
                    tikz_string = extra_tikz.format(source=source,coordinatetopivot=coordinate_to_pivot,goal=goal)
                    print("The first extended tikz line computed is: "+total_tikz_scope + coordinates +tikz_string)
                    tikz_code.append(total_tikz_scope + coordinates +tikz_string)


                print(tikz_code)

            #Let's store all the tikz codes once and for all:
            normal_lines_tikz = ""
            extended_lines_tikz = ""
            tikz_code_normal_lines =""
            if normal_lines_dictionary:
                for key, value in normal_lines_dictionary.items():
                    nodes = key.split(',')
                    print(nodes)
                    if len(nodes) == 2:
                        source = nodes[0].strip()
                        print(source)
                        goal = nodes[1].strip()
                        print(goal)
                        tikz_code_normal_lines = tikz_string_template.format(source=source, goal=goal)
                        print(tikz_code_normal_lines)
                        normal_lines_tikz += tikz_code_normal_lines
                        print(normal_lines_tikz)
                    else:
                        print("Invalid pair: ", pair)

            if eccedenze_dictionary:
                assembling_modulating_formula(eccedenze_dictionary)

                for code in tikz_code:
                    extended_lines_tikz += code

            print("The extended tikz lines are: "+ extended_lines_tikz)

            print("The tikz code is: " + str(tikz_code_normal_lines))
            latex_document = latex_template.replace("{user_input}", corrected_string)
            latex_document = latex_document.replace("{movement_strings}", normal_lines_tikz+extended_lines_tikz)

            #####cut here#####

            print("Latex document:", latex_document)  # Debug print

            # Writing the LaTeX code to a file again
            with open("document.tex", "w") as file:
                file.write(latex_document)

            
            try:
                # Running pdflatex with a timeout to avoid hanging
                result = subprocess.run(["pdflatex", "document.tex"], timeout=30, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # If the return code indicates an error, handle it
                if result.returncode != 0:
                    print("pdflatex failed with return code:", result.returncode)
                    print("Standard Output:", result.stdout.decode())
                    print("Standard Error:", result.stderr.decode())
                    raise subprocess.CalledProcessError(result.returncode, "pdflatex")
            except subprocess.CalledProcessError as e:
                print("An error occurred while generating the PDF:", e)
                flash("PDF generation failed. Please check your input for invalid characters. See the guide for more information.", "error_pdf_generation")
                return redirect(url_for('index'))  # Replace 'index' with your main page's route
            except subprocess.TimeoutExpired as e:
                print("The pdflatex command timed out:", e)
                flash("PDF generation timed out. Please check your input for invalid characters. See the guide for more information.", "error_timeout")  # Flash the error message
                return redirect(url_for('index'))  # Replace 'index' with your main page's route

            def pdf_to_transparent_image(pdf_path, output_path, page_number=0, zoom_factor=2.0):
                # Open the PDF file
                pdf_document = fitz.open(pdf_path)
                
                # Select the page
                page = pdf_document.load_page(page_number)
                
                # Define the zoom matrix
                zoom_matrix = fitz.Matrix(zoom_factor, zoom_factor)
                
                # Convert the page to a pixmap with the specified zoom factor
                pix = page.get_pixmap(matrix=zoom_matrix)
                
                # Convert pixmap to an image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Convert to RGBA
                img = img.convert("RGBA")
                
                # Make the white background transparent
                datas = img.getdata()
                new_data = []
                
                for item in datas:
                    # Change all white (also shades of whites)
                    # to transparent
                    if item[:3] == (255, 255, 255):
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)
                
                img.putdata(new_data)
                
                # Save the image
                img.save(output_path, "PNG")

            session['latex_document'] = latex_document
            # Check if the PDF was created successfully
            if os.path.exists("document.pdf"):
                print("PDF successfully created.")
                                    
            
                # Example usage:
                pdf_path = 'document.pdf'
                output_path = 'static/download/css/output-1.png'
                pdf_to_transparent_image(pdf_path, output_path, zoom_factor=4.0)  # Increase the zoom factor to increase resolution

                with Image.open(output_path) as img:
                    width, height = img.size

                print(f"PNG Width before resizing: {width}, Height: {height}")

                highest_value_size = []
            
                if width>height:
                    highest_value_size.append("width")
                    highest_value_size.append(width)
                else:
                    highest_value_size.append("height")
                    highest_value_size.append(height)
                
                print("The higher value is: "+ str(highest_value_size))

                def resize_image(input_path, output_path, fixed_width=418, fixed_height=383):

                
                    # Open the image
                    img = Image.open(input_path)
                    width, height = img.size

                    # Determine the highest dimension
                    
                    scale_factor = fixed_height / float(height)
                    new_width = int(width * scale_factor)
                    new_height = fixed_height

                    # Resize the image
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # Save the resized image
                    resized_img.save(output_path)

                # Example usage:
                resize_image(output_path, output_path)
                with Image.open(output_path) as img:
                    width, height = img.size

                print(f"PNG Width after resizing: {width}, Height: {height}")

                source_file = os.path.join(app.root_path, 'static\download\css', 'output-1.png')
    
                # Define the destination directory
                destination_folder = os.path.join(app.root_path, 'static\download-mobile\css')
                
                # Ensure the destination folder exists
                if not os.path.exists(destination_folder):
                    print("destination does not exists")
                
                # Define the destination file path
                destination_file = os.path.join(destination_folder, 'output-1.png')
                
                shutil.copy2(source_file, destination_file)

                return redirect(url_for('download'))
            else:
                print("PDF generation failed.")
                # Handle the error appropriately
                flash("PDF generation failed.", "error_pdf_generation")
                return redirect(url_for('index'))


        else:
            print(" ")
            print("---------------LINE DIRECTIONS DEFINED---------------")
            print(" ")
            print(" ")
            print("---------------USER'S INPUT---------------")
            print(" ")
            print("The structure submitted is: " + user_input)
            print("The number of movements required is: " + str(movement))  
            print("The labels of the goals are: " + from_nodes)
            print("The labels of the probes are: " + to_nodes)
            print("The directions from the goals are: " + direction_out)
            print("The directions to the probes are: " + direction_in)
            print("---------------PREPROCESSED INPUT---------------")
            print("The node pairs are the following: " + str(node_pairs))
            print("The direction pairs are the following: " + str(direction_pairs))
            print(" ")

            #latex_template
            tikz_code_with_directions_template = r"\draw[->,dotted] ({source}) to[out={out},in={in_dir}]({goal});"

            ### ASSOCIATING DIRECTIONS TO EACH NODE ###

            extended_lines_tikz = ""
            for i in range(len(node_pairs)):  #['DP3, DP', 'T, does', 'DP2, DP1']       # ['north-west, south-west', 'west, west', 'south-east, north-east']
                source = node_pairs[i].split(',')[0]
                goal = node_pairs[i].split(',')[1]
                out = direction_pairs[i].split(',')[0]
                in_dir = direction_pairs[i].split(',')[1]
                tikz_coord = tikz_code_with_directions_template.format(source=source,out=out,in_dir=in_dir,goal=goal)
                extended_lines_tikz += tikz_coord

        
            print("The extended tikz lines are: "+ extended_lines_tikz)

     
            latex_document = latex_template.replace("{user_input}", corrected_string)
            latex_document = latex_document.replace("{movement_strings}", extended_lines_tikz)

            #####cut here#####

            print("Latex document:", latex_document)  # Debug print

            # Writing the LaTeX code to a file again
            with open("document.tex", "w") as file:
                file.write(latex_document)

            
            try:
                # Running pdflatex with a timeout to avoid hanging
                result = subprocess.run(["pdflatex", "document.tex"], timeout=30, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # If the return code indicates an error, handle it
                if result.returncode != 0:
                    print("pdflatex failed with return code:", result.returncode)
                    print("Standard Output:", result.stdout.decode())
                    print("Standard Error:", result.stderr.decode())
                    raise subprocess.CalledProcessError(result.returncode, "pdflatex")
            except subprocess.CalledProcessError as e:
                print("An error occurred while generating the PDF:", e)
                flash("PDF generation failed. Please check your input for invalid characters. See the guide for more information.", "error_pdf_generation")
                return redirect(url_for('index'))  # Replace 'index' with your main page's route
            except subprocess.TimeoutExpired as e:
                print("The pdflatex command timed out:", e)
                flash("PDF generation timed out. Please check your input for invalid characters. See the guide for more information.", "error_timeout")  # Flash the error message
                return redirect(url_for('index'))  # Replace 'index' with your main page's route

            def pdf_to_transparent_image(pdf_path, output_path, page_number=0, zoom_factor=2.0):
                # Open the PDF file
                pdf_document = fitz.open(pdf_path)
                
                # Select the page
                page = pdf_document.load_page(page_number)
                
                # Define the zoom matrix
                zoom_matrix = fitz.Matrix(zoom_factor, zoom_factor)
                
                # Convert the page to a pixmap with the specified zoom factor
                pix = page.get_pixmap(matrix=zoom_matrix)
                
                # Convert pixmap to an image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Convert to RGBA
                img = img.convert("RGBA")
                
                # Make the white background transparent
                datas = img.getdata()
                new_data = []
                
                for item in datas:
                    # Change all white (also shades of whites)
                    # to transparent
                    if item[:3] == (255, 255, 255):
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)
                
                img.putdata(new_data)
                
                # Save the image
                img.save(output_path, "PNG")

            session['latex_document'] = latex_document
            # Check if the PDF was created successfully
            if os.path.exists("document.pdf"):
                print("PDF successfully created.")
                                    
            
                # Example usage:
                pdf_path = 'document.pdf'
                output_path = 'static/download/css/output-1.png'
                pdf_to_transparent_image(pdf_path, output_path, zoom_factor=4.0)  # Increase the zoom factor to increase resolution

                with Image.open(output_path) as img:
                    width, height = img.size

                print(f"PNG Width before resizing: {width}, Height: {height}")

                highest_value_size = []
            
                if width>height:
                    highest_value_size.append("width")
                    highest_value_size.append(width)
                else:
                    highest_value_size.append("height")
                    highest_value_size.append(height)
                
                print("The higher value is: "+ str(highest_value_size))
                ua = session.get('ua')
                def resize_image(input_path, output_path, fixed_width=418, fixed_height=383):
                  
                    # Open the image
                    img = Image.open(input_path)
                    width, height = img.size

                    # Determine the highest dimension
                    
                    scale_factor = fixed_height / float(height)
                    new_width = int(width * scale_factor)
                    new_height = fixed_height

                    # Resize the image
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # Save the resized image
                    resized_img.save(output_path)

                # Example usage:
                resize_image(output_path, output_path)
                with Image.open(output_path) as img:
                    width, height = img.size

                print(f"PNG Width after resizing: {width}, Height: {height}")

                source_file = os.path.join(app.root_path, 'static\download\css', 'output-1.png')
    
                # Define the destination directory
                destination_folder = os.path.join(app.root_path, 'static\download-mobile\css')
                
                # Ensure the destination folder exists
                if not os.path.exists(destination_folder):
                    print("destination does not exists")
                
                # Define the destination file path
                destination_file = os.path.join(destination_folder, 'output-1.png')
                
                shutil.copy2(source_file, destination_file)

                return redirect(url_for('download'))
            
    ########### NOW CONVERT IT TO PDF AND PNG######################################        
    return redirect(url_for('download'))


@app.route('/download')
def download():
    user_agent = request.headers.get('User-Agent')
    ua = parse(user_agent)
    if ua.is_mobile:
        response = make_response(render_template('download-mobile.html'))
        # Set headers to disable caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    else:
        response = make_response(render_template('download.html'))
        # Set headers to disable caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response


@app.route('/latex')
def show_latex():
    latex_document = session.get('latex_document', 'Default content if not set')
    return render_template('latex_template.html', latex_content=latex_document)


@app.route('/get-pdf')
def get_pdf():
    # This route is responsible for actually serving the PDF file
    try:
        pdf_path = session.get('pdf_path', 'document.pdf')  # Fallback to 'document.pdf' if not set
        return send_file(pdf_path, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/get-png')
def get_png():
    # This route is responsible for actually serving the PDF file
    try:
        png_path = session.get('output_path', 'static\download\css\output-1.png')  # Fallback to 'document.pdf' if not set
        print("PNG file fetched for download")
        return send_file(png_path, as_attachment=True)
    except FileNotFoundError:
        abort(404)

if __name__ == "__main__":  # Make sure to use __name__ instead of name
    app.run(debug=True)
