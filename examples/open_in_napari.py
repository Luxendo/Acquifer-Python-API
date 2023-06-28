from acquifer.utils import array_from_directory

dataset_directory = input("Path to a IM dataset directory : ")
array = array_from_directory(dataset_directory)

print(array)