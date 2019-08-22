import re

str = 'https://sports.163.com/19/0707/12/EJG170GT0005877V.html'
results = re.findall('^https?://.*?/19/[0-9]{4}/[0-9]{2}/(.*)?.html', str, re.S)
print(results)