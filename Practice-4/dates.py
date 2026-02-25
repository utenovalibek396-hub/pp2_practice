import datetime
x = datetime.datetime.now()
print(x.year)
print(x.strftime("%A"))
# Second line gets the current date and time from your computer and stores it in variable x.
# strftime() formats the date into a readable string. "%A" means full weekday name.