Разработка рекомендательной системы

Matrix factorization in Python is primarily used for recommender systems (collaborative filtering) and dimensionality reduction. 
It involves decomposing a large matrix into two or more smaller, lower-rank matrices whose product approximates the original

https://www.nvidia.com/en-us/glossary/recommendation-system/

from sklearn.decomposition import NMF
import numpy as np

# Sample 4x3 matrix
X = np.array([[1, 1, 0], [2, 1, 0], [0, 1, 2], [0, 1, 3]])

# Decompose into 2 latent features
model = NMF(n_components=2, init='random', random_state=0)
W = model.fit_transform(X)  # User/Basis matrix
H = model.components_      # Item/Coefficient matrix

# Reconstruct the original matrix
print(np.dot(W, H))
