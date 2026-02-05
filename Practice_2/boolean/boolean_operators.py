n = int(input("Enter your numnber: "))
if n > 10 and n % 2 == 0:
    print("Yes")
if n > 10 or n % 2 == 0:
    print("Ok")
if not(n > 10):
    print("...")
# and - requires two conditions to be met
# or - if one of the two conditions is met
# not - negates