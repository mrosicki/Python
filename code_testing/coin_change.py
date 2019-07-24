coin = [50, 20, 10, 5, 2, 1]

def num_of_coins(amount,denominations):
    count_of_coins = 0
    coin_dict = dict.fromkeys(denominations)
    while amount>0:
        for coin in denominations:
            count_of_coins += amount // coin
            coin_dict[coin] = amount // coin
            amount = amount % coin
    return count_of_coins, coin_dict


print(num_of_coins(700,coin))