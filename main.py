import asyncio
from inventory import Inventory


def display_catalogue(catalogue):
    burgers = catalogue["Burgers"]
    sides = catalogue["Sides"]
    drinks = catalogue["Drinks"]

    print("--------- Burgers -----------\n")
    for burger in burgers:
        item_id = burger["id"]
        name = burger["name"]
        price = burger["price"]
        print(f"{item_id}. {name} ${price}")

    print("\n---------- Sides ------------")
    for side in sides:
        sizes = sides[side]

        print(f"\n{side}")
        for size in sizes:
            item_id = size["id"]
            size_name = size["size"]
            price = size["price"]
            print(f"{item_id}. {size_name} ${price}")

    print("\n---------- Drinks ------------")
    for beverage in drinks:
        sizes = drinks[beverage]

        print(f"\n{beverage}")
        for size in sizes:
            item_id = size["id"]
            size_name = size["size"]
            price = size["price"]
            print(f"{item_id}. {size_name} ${price}")

    print("\n------------------------------\n")


async def main():
    async def welcome_customer():
        print('Welcome to the ProgrammingExpert Burger Bar!')
        inventory = Inventory()
        print('Loading catalogue...')
        catalogue = await inventory.get_catalogue()
        display_catalogue(catalogue)
        return inventory

    async def get_order_items(inventory):
        print('Please enter the number of items that you would like to add to your order. Enter q to complete your order.')
        order_items = []
        while True:
            order_item = input('Enter an item number: ')
            if order_item == 'q':
                print('Placing order...')
                for order_item in order_items:
                    if not await inventory.decrement_stock(order_item):
                        order_items.remove(order_item)
                        print(f'Unfortunately item number {order_item} is out of stock and has been removed from your order. Sorry!')
                break
            if not order_item.isnumeric():
                print('Please enter a valid number.')
            elif int(order_item) < 1:
                print('Please enter a valid number.')
            elif int(order_item) > 20:
                print('Please enter a number below 21.')
            else:
                order_items.append(int(order_item))
        return order_items
    
    async def get_order_summary(inventory, order_items):
        order_summary_cors = []
        order_summary = []
        print('\nHere is a summary of your order:\n')
        order_summary_cors = [inventory.get_item(order_item) for order_item in order_items]
        order_summary = list(await asyncio.gather(*order_summary_cors))
        return order_summary

    async def collect_payment(order_summary):
        burgers = [order_details for order_details in order_summary if order_details['category'] == 'Burgers']
        sides = [order_details for order_details in order_summary if order_details['category'] == 'Sides']
        drinks = [order_details for order_details in order_summary if order_details['category'] == 'Drinks']
        for category in [burgers, sides, drinks]:
            category.sort(reverse=True, key=lambda x: x['price'])
        
        combos = list(zip(burgers, sides, drinks))
        for combo in combos:
            for item in combo:
                order_summary.remove(item)
        
        subtotal = 0
        for combo in combos:
            combo_price = round(sum([combo[i]['price'] for i in range(3)]) * 0.85, 2)
            print(f'${combo_price} Burger Combo')
            print(f'  {combo[0]["name"]}')
            print(f'  {combo[1]["size"]} {combo[1]["subcategory"]}')
            print(f'  {combo[2]["size"]} {combo[2]["subcategory"]}')
            subtotal += combo_price
        
        for item in order_summary:
            if item['category'] == 'Burgers':
                item_label = item['name']
            else:
                item_label = f"{item['size']} {item['subcategory']}"
            print(f"${item['price']} {item_label}")
            subtotal += item['price']
        subtotal = round(subtotal, 2)
        another_order = False
        tax_rate = 0.05
        tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax, 2)
        print(f'\nSubtotal: ${subtotal}')
        print(f'Tax: ${tax}')
        print(f'Total: ${total}')
        purchase_order_decision = input(f'Would you like to purchase this order for ${total} (yes/no)? ')
        if purchase_order_decision == 'no':
            print('No problem, please come again!')
            return
        else:
            print('Thank you for your order!')
            another_order_decision = input('Would you like to make another order (yes/no)? ')
            another_order = another_order_decision == 'yes'
        return another_order


    inventory = await welcome_customer()
    while True:
        order_items = await get_order_items(inventory)
        order_summary = await get_order_summary(inventory, order_items)
        another_order = await collect_payment(order_summary)
        if not another_order:
            break
    
    print('Goodbye!')
    return


if __name__ == "__main__":
    asyncio.run(main())
