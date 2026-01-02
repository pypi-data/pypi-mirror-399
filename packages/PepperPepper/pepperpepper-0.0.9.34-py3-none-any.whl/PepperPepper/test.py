from PepperPepper.MOT.callbacks import get_args_parser_train

if __name__ == "__main__":
    parser = get_args_parser_train()
    args = parser.parse_args()
    print(args)
    # You can add more code here to utilize the parsed arguments as needed.
    # For example, you might want to print the arguments or use them in a function.
    # print(args)
    # Example: print(f"Training with dataset: {args.dataset} and batch size: {args.batch_size}")                