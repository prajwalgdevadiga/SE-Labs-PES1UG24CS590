def parse_order(text):
    garment, kg = text.split(':')
    return garment.strip().title(), float(kg)

def weight_average(weights_csv):
    values = [int(r) for r in weights_csv.split(',')]
    return sum(values) // len(values)

def payable_charge(text):
    charge, discount = text.split('|')
    total = float(charge) * 1.18 - float(discount)
    return max(total, 0)

def main():
    print("==== Running parse_order ====")
    user_input = input("Enter garment:weight in kg (e.g. regular:6): ")
    result = parse_order(user_input)
    print("Garment and Weight:", result)

    print("\n==== Running weight_average ====")
    user_input = input("Enter garment weights as CSV (e.g. 3,5,8): ")
    result = weight_average(user_input)
    print("Average Weight:", result)

    print("\n==== Running payable_charge ====")
    user_input = input("Enter charge|discount (e.g. 300|40): ")
    result = payable_charge(user_input)
    print("Payable Charge:", result)

if __name__ == "__main__":
    main()
