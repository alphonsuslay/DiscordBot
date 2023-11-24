import discord
from discord.ext import commands, tasks
import json
from datetime import datetime

class Store(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.load_order_counter()  # Load the order counter from a file

    def load_order_counter(self):
        try:
            with open("json/order_counter.json", "r") as file:
                data = json.load(file)
                self.order_counter = data.get("counter", 1)
        except FileNotFoundError:
            # If the file doesn't exist, initialize the counter to 1
            self.order_counter = 1

    def save_order_counter(self):
        data = {"counter": self.order_counter}
        with open("json/order_counter.json", "w") as file:
            json.dump(data, file)
    
    @staticmethod
    def load_config():
        with open("settings/config.json", "r") as file:
            config = json.load(file)
        return config

    @commands.Cog.listener()
    async def on_ready(self):
        print("store.py is online")
    
    @commands.command(aliases = ["store"])
    async def shop(self, ctx):
        # Load product data from the JSON file
        with open("json\stock.json", "r") as file:
            products = json.load(file)

        # Create an embed to display product information
        embed = discord.Embed(title="Product List", color=discord.Color.blue())

        for product_name, product_info in products.items():
            code = product_info["Code"]
            quantity = product_info["Quantity"]
            price = product_info["Price"]
            embed.add_field(name=product_name, value=f"<:blank_arrow:1155167090261622844> Code: {code}\n <:blank_arrow:1155167090261622844> Quantity: {quantity} \n <:blank_arrow:1155167090261622844> Price: ${price}", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def addproduct(self, ctx, product_name, code, quantity, price: int):  # Specify that price is an integer
        # Ensure that the user has the necessary permissions to use this command (customize this part)
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("You don't have permission to use this command.")

        # Load existing product data from stock.json
        try:
            with open("json/stock.json", "r") as file:
                products = json.load(file)
        except FileNotFoundError:
            products = {}  # Create an empty dictionary if the file doesn't exist

        # Check if the product name already exists
        if product_name in products:
            return await ctx.send("A product with that name already exists.")

        # Add the new product information to the data
        products[product_name] = {"Code": code, "Quantity": quantity, "Price": price}  # Convert price to an integer

        # Write the updated data back to stock.json
        with open("json/stock.json", "w") as file:
            json.dump(products, file, indent=4)

        await ctx.send(f"Product '{product_name}' has been added to the store.")

    @commands.command()
    async def removeproduct(self, ctx, product_identifier):
        # Ensure that the user has the necessary permissions to use this command (customize this part)
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("You don't have permission to use this command.")

        # Load existing product data from stock.json
        try:
            with open("json/stock.json", "r") as file:
                products = json.load(file)
        except FileNotFoundError:
            return await ctx.send("The product data file does not exist.")

        # Check if the provided product identifier exists in the products
        if product_identifier not in products:
            return await ctx.send("Product not found. Please provide a valid product name.")

        # Remove the product from the data
        removed_product = products.pop(product_identifier)

        # Write the updated data back to stock.json
        with open("json/stock.json", "w") as file:
            json.dump(products, file, indent=4)

        await ctx.send(f"Product '{product_identifier}' has been removed from the store.")

    @commands.command()
    async def addstock(self, ctx, identifier, quantity: int):
        # Ensure that the user has the necessary permissions to use this command (administrator)
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("You don't have permission to use this command.")

        # Load existing product data from stock.json
        try:
            with open("json/stock.json", "r") as file:
                products = json.load(file)
        except FileNotFoundError:
            return await ctx.send("The product data file does not exist.")

        # Check if the identifier matches any product name or code
        found_product = None
        for product_name, product_info in products.items():
            if product_name.lower() == identifier.lower() or product_info.get("Code", "").lower() == identifier.lower():
                found_product = product_name
                break

        if found_product is None:
            return await ctx.send("Product not found. Please provide a valid product name or code.")

        # Update the quantity of the found product, ensuring it's an integer
        products[found_product]["Quantity"] = int(products[found_product]["Quantity"]) + quantity

        # Write the updated data back to stock.json
        with open("json/stock.json", "w") as file:
            json.dump(products, file, indent=4)

        await ctx.send(f"Added {quantity} to the quantity of '{found_product}'.")
 
    @commands.command()
    async def removestock(self, ctx, identifier, quantity: int):
        # Ensure that the user has the necessary permissions to use this command (administrator)
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("You don't have permission to use this command.")

        # Load existing product data from stock.json
        try:
            with open("json/stock.json", "r") as file:
                products = json.load(file)
        except FileNotFoundError:
            return await ctx.send("The product data file does not exist.")

        # Check if the identifier matches any product name or code
        found_product = None
        for product_name, product_info in products.items():
            if product_name.lower() == identifier.lower() or product_info.get("Code", "").lower() == identifier.lower():
                found_product = product_name
                break

        if found_product is None:
            return await ctx.send("Product not found. Please provide a valid product name or code.")

        # Ensure that the quantity to remove is a positive integer
        if not isinstance(quantity, int) or quantity <= 0:
            return await ctx.send("Please provide a valid positive integer quantity to remove.")

        # Check if there's enough quantity to remove
        current_quantity = products[found_product].get("Quantity", 0)
        if quantity > current_quantity:
            return await ctx.send(f"There's not enough quantity of '{found_product}' to remove.")

        # Update the quantity of the found product
        products[found_product]["Quantity"] -= quantity

        # Write the updated data back to stock.json
        with open("json/stock.json", "w") as file:
            json.dump(products, file, indent=4)

        await ctx.send(f"Removed {quantity} from the quantity of '{found_product}'.")

    @commands.command()
    async def removeorder(self, ctx, order_id):
        # Ensure that the user has the necessary permissions to use this command (administrator)
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("You don't have permission to use this command.")

        # Load existing orders from the JSON file
        try:
            with open("json/orders.json", "r") as file:
                orders = json.load(file)
        except FileNotFoundError:
            return await ctx.send("The orders data file does not exist.")
        except json.JSONDecodeError:
            orders = []

        # Ensure that orders is a list (initialize as an empty list if not)
        if not isinstance(orders, list):
            orders = []

        # Find the order with the specified order ID
        found_order = None

        for order in orders:
            if order.get("Order ID", "") == order_id:
                found_order = order
                break

        if not found_order:
            return await ctx.send("Order not found. Please provide a valid order ID.")

        # Remove the found order from the list of orders
        orders.remove(found_order)

        # Write the updated data back to orders.json
        with open("json/orders.json", "w") as file:
            json.dump(orders, file, indent=4)

        await ctx.send(f"Order {order_id} has been removed.")

    @commands.command()
    async def order(self, ctx, product_identifier, quantity: int):
        # Load product data from the JSON file
        try:
            with open("json/stock.json", "r") as file:
                products = json.load(file)
        except FileNotFoundError:
            return await ctx.send("The product data file does not exist.")
        except json.JSONDecodeError:
            # Handle the case where the file exists but is empty or not valid JSON
            products = {}

        # Check if the product identifier is valid (either product name or product code)
        if product_identifier in products:
            # If the provided identifier is a product name
            product_name = product_identifier
            product_code = products[product_name]["Code"]
        else:
            # If the provided identifier is a product code
            matching_products = [name for name, info in products.items() if info.get("Code") == product_identifier]
            if not matching_products:
                return await ctx.send("Invalid product name or code. Please provide a valid product name or code.")

            # Use the first matching product name found
            product_name = matching_products[0]
            product_code = product_identifier  # Use the provided product code

        # Check if there is enough quantity in stock
        if products[product_name]["Quantity"] < quantity:
            return await ctx.send("There are not enough stock to fulfill your order.")

        # Generate the order ID based on the current order counter
        order_id = f"PO-{str(self.order_counter).zfill(3)}"

        # Create a record of the order with order ID
        order_data = {
            "Order ID": order_id,
            "User": str(ctx.author),
            "Code": product_code,
            "Quantity": quantity
        }

        # Increment the order ID counter for the next order
        self.order_counter += 1

        # Save the updated order counter to a file
        self.save_order_counter()

        # Load existing orders or initialize as an empty list
        try:
            with open("json/orders.json", "r") as file:
                orders = json.load(file)
        except FileNotFoundError:
            orders = []

        # Ensure that orders is a list (initialize as empty list if not)
        if not isinstance(orders, list):
            orders = []

        # Append the order to the list of orders
        orders.append(order_data)

        with open("json/orders.json", "w") as file:
            json.dump(orders, file, indent=4)

        await ctx.send(f"Order {order_id} placed successfully for {quantity} units of {product_code}.")

    @commands.command()
    @commands.has_permissions(administrator=True)  # Ensure the user has administrator permissions
    async def vieworder(self, ctx, order_id=None):
        # Load existing orders from the JSON file
        try:
            with open("json/orders.json", "r") as file:
                orders = json.load(file)
        except FileNotFoundError:
            return await ctx.send("The orders data file does not exist.")
        except json.JSONDecodeError:
            orders = []

        # Ensure that orders is a list (initialize as an empty list if not)
        if not isinstance(orders, list):
            orders = []

        if order_id:
            # Display a specific order
            found_order = None
            for order in orders:
                if order.get("Order ID", "") == order_id:
                    found_order = order
                    break

            if found_order:
                product_code = found_order.get("Product Code", "N/A")

                embed = discord.Embed(
                    title=f"Order Information for {order_id}",
                    color=discord.Color.blue(),
                )

                embed.add_field(
                    name="User",
                    value=found_order.get("User", "N/A"),
                    inline=False,
                )
                embed.add_field(
                    name="Product Code",
                    value=product_code if product_code else "N/A",
                    inline=False,
                )
                embed.add_field(
                    name="Quantity",
                    value=found_order.get("Quantity", "N/A"),
                    inline=False,
                )

                await ctx.send(embed=embed)
            else:
                await ctx.send("Order not found. Please provide a valid order ID.")
        else:
            # Display all orders
            if len(orders) > 0:
                embed = discord.Embed(
                    title="All Orders",
                    color=discord.Color.blue(),
                )

                for order in orders:
                    product_code = order.get("Product Code", "N/A")

                    embed.add_field(
                        name=f"Order ID: {order.get('Order ID', 'N/A')}",
                        value=f"User: {order.get('User', 'N/A')}\nProduct Code: {product_code if product_code else 'N/A'}\nQuantity: {order.get('Quantity', 'N/A')}",
                        inline=False,
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("No orders available.")

    @commands.command()
    async def complete(self, ctx, order_id):
        config = self.load_config()
        purchase_hist_channel_id = int(config.get("PURCHASEHIST_CHANNEL", 0))
        purchase_hist_channel = self.client.get_channel(purchase_hist_channel_id)

        if purchase_hist_channel is None:
            return await ctx.send("Purchase history channel not found. Please check the channel ID in config.")
        
        # Load existing orders from the JSON file
        try:
            with open("json/orders.json", "r") as file:
                orders = json.load(file)
        except FileNotFoundError:
            return await ctx.send("The orders data file does not exist.")
        except json.JSONDecodeError:
            orders = []

        # Ensure that orders is a list (initialize as an empty list if not)
        if not isinstance(orders, list):
            orders = []

        # Find the order with the specified order ID
        found_order = None

        for order in orders:
            if order.get("Order ID", "") == order_id:
                found_order = order
                break

        if not found_order:
            return await ctx.send("Order not found. Please provide a valid order ID.")

        # Remove the found order from the list of orders
        orders.remove(found_order)

        # Write the updated data back to orders.json
        with open("json/orders.json", "w") as file:
            json.dump(orders, file, indent=4)

        # Load completed orders or initialize as an empty list
        try:
            with open("json/completed.json", "r") as file:
                completed_orders = json.load(file)
        except FileNotFoundError:
            completed_orders = []

        if not isinstance(completed_orders, list):
            completed_orders = []

        # Append the found order to the list of completed orders
        completed_orders.append(found_order)

        # Write the updated data back to completed.json
        with open("json/completed.json", "w") as file:
            json.dump(completed_orders, file, indent=4)

        # Call the send_history_order_embed function to send the embed message
        await self.send_history_order_embed(ctx, found_order) 

        # Update stock quantity
        await self.update_stock(order_id)

        await ctx.send(f"Order {order_id} has been completed and moved to the completed list.")

    async def send_history_order_embed(self, ctx, order_data):
        config = self.load_config()
        history_order_channel_id = int(config.get("PURCHASEHIST_CHANNEL", 0))
        history_order_channel = ctx.guild.get_channel(history_order_channel_id)

        if history_order_channel is None:
            return await ctx.send("History order channel not found. Please check the channel ID in config.")

        # Create an embed with order details
        embed = discord.Embed(
            title="Order Completed",
            description=f"**Order ID:** {order_data['Order ID']}\n**User:** {order_data['User']}\n**Quantity:** {order_data['Quantity']}",
            color=discord.Color.green(),
        )
        embed.set_footer(text="Thank you for purchasing!")

        # Send the embed to the history order channel
        await history_order_channel.send(embed=embed)
    
    async def update_stock(self, order_id):
        with open('json/stock.json', 'r') as file:
            stock = json.load(file)

        found = False  # Flag to track if the product was found

        for code, data in stock.items():
            if data['Code'] == order_id:
                found = True
                stock[code]['Quantity'] -= 1  # Reduce quantity for the matched product

        if found:
            # Update the stock.json file
            with open('json/stock.json', 'w') as file:
                json.dump(stock, file, indent=4)
        else:
            print(f"Product {order_id} not found in stock.")
                
    @commands.command()
    async def myorder(self, ctx):
        # Load existing orders from the JSON file
        try:
            with open("json/orders.json", "r") as file:
                orders = json.load(file)
        except FileNotFoundError:
            orders = []

        # Ensure that orders is a list (initialize as an empty list if not)
        if not isinstance(orders, list):
            orders = []

        # Filter orders for the current user
        user_orders = [order for order in orders if order.get("User") == str(ctx.author)]

        if len(user_orders) > 0:
            embed = discord.Embed(
                title="Your Orders",
                color=discord.Color.blue(),
            )

            for order in user_orders:
                product_code = order.get("Product Code", "N/A")

                embed.add_field(
                    name=f"Order ID: {order.get('Order ID', 'N/A')}",
                    value=f"Product Code: {product_code if product_code else 'N/A'}\nQuantity: {order.get('Quantity', 'N/A')}",
                    inline=False,
                )

            await ctx.send(embed=embed)
        else:
            await ctx.send("You don't have any orders.")

    @commands.command()
    @commands.has_permissions(administrator=True)  # Ensure the user has administrator permissions
    async def editproduct(self, ctx, old_product_name, new_product_name, product_code):
        # Load existing product data from stock.json
        try:
            with open("json/stock.json", "r") as file:
                products = json.load(file)
        except FileNotFoundError:
            return await ctx.send("The product data file does not exist.")
        except json.JSONDecodeError:
            # Handle the case where the file exists but is empty or not valid JSON
            products = {}

        # Check if the old product name exists
        if old_product_name not in products:
            return await ctx.send("The old product name does not exist. Please provide a valid product name.")

        # Update the product information
        product_info = products.pop(old_product_name)  # Remove the old entry
        product_info["Code"] = product_code
        products[new_product_name] = product_info

        # Write the updated data back to stock.json
        with open("json/stock.json", "w") as file:
            json.dump(products, file, indent=4)

        await ctx.send(f"Product '{old_product_name}' has been edited to '{new_product_name}' with the code '{product_code}'.")

    @commands.command()
    async def cancelorder(self, ctx, order_id):
        # Load existing orders from the JSON file
        try:
            with open("json/orders.json", "r") as file:
                orders = json.load(file)
        except FileNotFoundError:
            return await ctx.send("The orders data file does not exist.")
        except json.JSONDecodeError:
            orders = []

        # Find the order with the specified order ID
        found_order = None

        for order in orders:
            if order.get("Order ID", "") == order_id:
                found_order = order
                break

        if not found_order:
            return await ctx.send("Order not found. Please provide a valid order ID.")

        # Check if the user requesting the cancellation is the same as the user who placed the order
        if str(ctx.author) != found_order.get("User", ""):
            return await ctx.send("You can only cancel your own orders.")

        # Remove the found order from the list of orders
        orders.remove(found_order)

        # Write the updated data back to orders.json
        with open("json/orders.json", "w") as file:
            json.dump(orders, file, indent=4)

        # Decrement the order counter by 1
        self.order_counter -= 1
        self.save_order_counter()

        await ctx.send(f"Order {order_id} has been canceled.")

def get_product_name(self, product_code):
    # Load product data from the JSON file
    try:
        with open("json/stock.json", "r") as file:
            products = json.load(file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        products = {}

    # Find the product name based on the product code
    for name, info in products.items():
        if info.get("Code", "") == product_code:
            return name

    return None


    @commands.command()
    @commands.has_permissions(administrator=True)  # Ensure the user has administrator permissions
    async def complete(self, ctx, order_id):
        # Load existing orders from the JSON file
        try:
            with open("json/orders.json", "r") as file:
                orders = json.load(file)
        except FileNotFoundError:
            return await ctx.send("The orders data file does not exist.")
        except json.JSONDecodeError:
            orders = []

        # Ensure that orders is a list (initialize as an empty list if not)
        if not isinstance(orders, list):
            orders = []

        # Find the order with the specified order ID
        found_order = None

        for order in orders:
            if order.get("Order ID", "") == order_id:
                found_order = order
                break

        if not found_order:
            return await ctx.send("Order not found. Please provide a valid order ID.")

        # Load existing stock data from the JSON file
        try:
            with open("json/stock.json", "r") as file:
                products = json.load(file)
        except FileNotFoundError:
            return await ctx.send("The product data file does not exist.")
        except json.JSONDecodeError:
            products = {}

        # Get the product code and quantity from the completed order
        product_code = found_order.get("Product Code", "")
        quantity = found_order.get("Quantity", 0)

        # Check if the product code is valid
        if product_code not in products.values():
            # Try to find the product code by name
            matching_products = [code for code, info in products.items() if info.get("Code") == product_code]
            if not matching_products:
                return await ctx.send(
                    "Invalid product code in the completed order. Please check the product code or name."
                )

            # Use the first matching product code found
            product_code = matching_products[0]

        # Deduct the quantity from the stock
        if products[product_code]["Quantity"] < quantity:
            return await ctx.send("There is not enough stock to fulfill this order.")

        products[product_code]["Quantity"] -= quantity

        # Write the updated stock data back to stock.json
        with open("json/stock.json", "w") as file:
            json.dump(products, file, indent=4)

        # Remove the found order from the list of orders
        orders.remove(found_order)

        # Write the updated data back to orders.json
        with open("json/orders.json", "w") as file:
            json.dump(orders, file, indent=4)

        # Save the completed order to completed.json
        try:
            with open("json/completed.json", "r") as file:
                completed_orders = json.load(file)
        except FileNotFoundError:
            completed_orders = []

        if not isinstance(completed_orders, list):
            completed_orders = []

        completed_orders.append(found_order)

        with open("json/completed.json", "w") as file:
            json.dump(completed_orders, file, indent=4)

        # Send an embedded message to history_order_channel_id
        await self.send_history_order_embed(ctx, found_order)

        await ctx.send(f"Order {order_id} has been completed and moved to the completed list.")

    async def send_history_order_embed(self, ctx, order_data):
        # Fetch the history order channel
        history_order_channel = ctx.guild.get_channel(history_order_channel_id)

        if history_order_channel is None:
            return await ctx.send("History order channel not found. Please check the channel ID.")

        # Create an embed with order details
        embed = discord.Embed(
            title="Order Completed",
            description=f"**Order ID:** {order_data['Order ID']}\n**User:** {order_data['User']}\n**Quantity:** {order_data['Quantity']}",
            color=discord.Color.green(),timestamp = ctx.message.created_at
        )
        embed.set_thumbnail(url = ctx.author.avatar)
        embed.set_footer(text = "Thank you for purchasing!", icon_url = ctx.author.avatar)


        # Send the embed to the history order channel
        await history_order_channel.send(embed=embed)

async def setup(client):
    await client.add_cog(Store(client))