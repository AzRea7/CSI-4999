import kagglehub

# Download the Housing Prices dataset by Yasser H.,
path = kagglehub.dataset_download('yasserh/housing-prices-dataset')

print(f" Dataset downloaded to: {path}")