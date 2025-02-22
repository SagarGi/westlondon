import matplotlib.pyplot as plt 
# x axis values  
x = [10 ,20 ,30]  
# corresponding y axis values  
y = [20 ,40 ,10]

# plotting the points in to the graph
plt.plot(x, y)

plt.xlabel('this x-axis')  
# naming the y axis  
plt.ylabel('this is y-axis')  
    
# giving a title to my graph  
plt.title('Matplotlib Graph Respresentation')  
    
# function to show the plot  
plt.show() 