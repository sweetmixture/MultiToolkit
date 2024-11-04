import matplotlib.pyplot as plt

# Example data points
x = [0, 1, 2, 3, 4]
y = [0, 1, 4, 9, 16]

# Create a plot
plt.plot(x, y, marker='o')

# Define the start and end points of the arrow
start_point = (0, 0)
end_point = (2, 2)

# Add an arrow from start_point to end_point
plt.annotate(
	'',  # No text for the annotation
	xy=end_point,  # End of the arrow
	xytext=start_point,  # Start of the arrow
	arrowprops=dict(facecolor='black', arrowstyle='->')  # Arrow style
)

# Add labels and title for clarity
plt.xlabel('x-axis')
plt.ylabel('y-axis')
plt.title('Arrow from one point to another')

# Show the plot
plt.show()

