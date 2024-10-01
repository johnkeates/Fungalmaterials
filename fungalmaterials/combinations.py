import plotly.graph_objects as go

# combination_list
	# [{'method': 'SSF', 'topic': 'Composite'}, {'method': 'SSF', 'topic': 'Composite'}, {'method': 'FB', 'topic': 'Pure'}, {'method': 'FB', 'topic': 'Amadou'}, {'method': 'LSF', 'topic': 'Composite'}]

# combinations
	# ['SSF-Composite', 'SSF-Composite', 'FB-Pure', 'FB-Amadou', 'LSF-Composite']

# count_combinations
	# {'SSF-Composite': 2, 'FB-Pure': 1, 'FB-Amadou': 1, 'LSF-Composite': 1}

def generate_sankey(combination_list):
	combinations = []

	for i in combination_list:
		# Check if 'method' and 'topic' exist in the dictionary
		if "method" in i and "topic" in i:
			# Combine method and topic
			combination = f"{i['method']}-{i['topic']}"
			# Add the combination to the list
			combinations.append(combination)


	count_combinations = {}

	for j in combinations:
		if j in count_combinations.keys():                            
			# print("combination present +1")
			count_combinations[j] = int(count_combinations[j]) + 1 
		else:                                        
			# print("combination not present add to dict")
			count_combinations[j]= 1


	# Use Plotly to make a sankey (aka alluvial) figure
	# Step 1: Create a set of unique labels
	labels_set = set()
	for key in count_combinations.keys():
		source, target = key.split('-')
		labels_set.add(source)
		labels_set.add(target)

	# Convert the set to a sorted list
	labels_list = sorted(labels_set)

	# If labels_list is empty sankey_fig should result empty and no figure gets displayed
	if not labels_list:
		sankey_fig = ''
	else:
		# Step 2: Create a mapping of labels to indices
		label_to_index = {label: idx for idx, label in enumerate(labels_list)}

		# Step 3: Create source, target, and value lists
		sources = []
		targets = []
		values = []

		# Initialize link colors list
		link_colors = []

		# Define colors based on methods
		method_colors = {
			"LSF": "rgba(158, 197, 254, 0.5)",  # 50% opacity
			"SSF": "rgba(241, 174, 181, 0.5)",  # 50% opacity
			"FB": "rgba(163, 207, 187, 0.5)"    # 50% opacity
		}

		# All topics should have the same color with 50% opacity
		topic_color = "rgba(233, 236, 239, 0.5)"  # 50% opacity

		for key, value in count_combinations.items():
			source, target = key.split('-')
			sources.append(label_to_index[source])
			targets.append(label_to_index[target])
			values.append(value)
			
			# Set link color based on the method
			link_color = method_colors.get(source, topic_color)  # Default to topic color if method not found
			link_colors.append(link_color)

		# Step 4: Define colors for the nodes
		colors = []
		for label in labels_list:
			if label in method_colors:
				# Set node color to full opacity
				colors.append(method_colors[label].replace(", 0.5)", ", 1)"))
			else:
				colors.append(topic_color.replace(", 0.5)", ", 1)"))

		# Step 5: Create the Sankey diagram
		fig = go.Figure(go.Sankey(
			node=dict(
				pad=25,
				thickness=25,
				label=labels_list,
				color=colors,
				hoverinfo = 'skip',
			),
			link=dict(
				source=sources,
				target=targets,
				value=values,
				color=link_colors,
				hovertemplate='%{source.label} & %{target.label}<br>%{value:d} articles<extra></extra><extra></extra>',
			)
		))

		# Step 6: Return the HTML string of the figure
		return fig.to_html(full_html=False,
			config=dict(
			displayModeBar=True,  # Show the mode bar (optional)
			modeBarButtonsToRemove=['toImage', 'select2d', 'lasso2d']  # Remove some buttons
			))