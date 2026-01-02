import homcloud.codebook


class PBoWSpec(homcloud.codebook.PBoW):
    """
    This class represents a specification of vectorization of persistence diagrams by
    persistence codebook's PBoW (persistence bag-of-words representation) method.

    K-Means is used for clustering.

    Args:
        n_random_sampled_pairs (int): The number of randomly sampled pairs used when calculating clusters.
        n_clusters (int): The number of clusters.
        weighting_function (Callable[[float, float], float] | None):
            Weighting function for sampling when calculating clusters.
        random_state (int | None): The random seed for random sampling.
        normalize (bool): The bow histogram is normalized when vectorizing a PD if True.

    References:
        * https://link.springer.com/article/10.1007/s10462-020-09897-4
        * https://github.com/bziiuj/pcodebooks

    Methods:
        fit(diagrams)
            Compute clusters in preparation for vectorization.

            Args:
                diagrams (list[:class:`PD`]): The list of digrams whose pairs are used for clustering.

        vectorize(self, diagram):
            Vecotrize a diagram.

            Args:
                diagrams (:class:`PD`): The diagram to be vecotrized.

            Returns:
                numpy.ndarary: A 1-dimensional array


    Attributes:
        cluster_centers (numpy.ndarary): The 2d array of centers of clusters.

    """

    pass


class StablePBoWSpec(homcloud.codebook.StablePBoW):
    """
    This class represents a specification of vectorization of persistence diagrams by
    persistence codebook's stable PBoW (persistence bag-of-words representation) method.

    Gaussian mixture model is used for clustering.

    Args:
        n_random_sampled_pairs (int): The number of randomly sampled pairs used when calculating clusters.
        n_clusters (int): The number of clusters.
        weighting_function (Callable[[float, float], float] | None):
            Weighting function for sampling when calculating clusters.
        random_state (int | None): The random seed for random sampling.
        normalize (bool): The bow histogram is normalized when vectorizing a PD if True.

    References:
        * https://link.springer.com/article/10.1007/s10462-020-09897-4
        * https://github.com/bziiuj/pcodebooks

    Methods:
        fit(diagrams)
            Compute clusters in preparation for vectorization.

            Args:
                diagrams (list[:class:`PD`]): The list of digrams whose pairs are used for clustering.

        vectorize(self, diagram):
            Vecotrize a diagram.

            Args:
                diagrams (:class:`PD`): The diagram to be vecotrized.

            Returns:
                numpy.ndarary: A 1-dimensional array

        plot_gmm_density_estimation(ax, x_range, x_num, y_range=None, y_num=None)
            Plot a gaussian mixture distribution in a matplotlib's axes.

            Args:
                ax (matplotlib.axes.Axes): Matplotlib's axes object to be plotted.
                x_range (tuple[float, float]): The X range.
                x_bins (int): The number of bins in the X direction.
                y_range (tuple[float, float]): The Y range. Same as x_range if None.
                y_bins (int): The number of bins in the Y direction. Same as x_bins if None.


    Attributes:
        cluster_centers (numpy.ndarary): The 2d array of centers of clusters (means of gaussian distributions)
        cluster_covariances (numpy.ndarary): The 3d array of covariances of clusters
                                             (covariance matrices of gaussian distributions)
    """

    pass


class PFVSpec(homcloud.codebook.StablePBoW):
    """
    This class represents a specification of vectorization of persistence diagrams by
    persistence codebook's PFV (persistence Fisher vector) method.

    Gaussian mixture model is used for clustering.

    Args:
        n_random_sampled_pairs (int): The number of randomly sampled pairs used when calculating clusters.
        n_clusters (int): The number of clusters.
        weighted_function (Callable[[float, float], float] | None):
            Weighting function for sampling when calculating clusters.
        random_state (int | None): The random seed for random sampling.
        normalize (bool): The bow histogram is normalized when vectorizing a PD if True.

    References:
        * https://link.springer.com/article/10.1007/s10462-020-09897-4
        * https://github.com/bziiuj/pcodebooks
        * https://www.vlfeat.org/api/fisher-fundamentals.html
        * F. Perronnin and C. Dance. Fisher kenrels on visual vocabularies
          for image categorizaton. In Proc. CVPR, 2006.
        * Florent Perronnin, Jorge Sánchez, and Thomas Mensink.
          Improving the fisher kernel for large-scale image classification. In Proc. ECCV, 2010.

    Methods:
        fit(diagrams)
            Compute clusters in preparation for vectorization.

            Args:
                diagrams (list[:class:`PD`]): The list of digrams whose pairs are used for clustering.

        vectorize(self, diagram)
            Vecotrize a diagram.

            Args:
                diagrams (:class:`PD`): The diagram to be vecotrized.

            Returns:
                numpy.ndarary: A 1-dimensional array

        plot_gmm_density_estimation(ax, x_range, x_num, y_range=None, y_num=None)
            Plot a gaussian mixture distribution in a matplotlib's axes.

            Args:
                ax (matplotlib.axes.Axes): Matplotlib's axes object to be plotted.
                x_range (tuple[float, float]): The X range.
                x_bins (int): The number of bins in the X direction.
                y_range (tuple[float, float]): The Y range. Same as x_range if None.
                y_bins (int): The number of bins in the Y direction. Same as x_bins if None.


    Attributes:
        cluster_centers (numpy.ndarary): The 2d array of centers of clusters (means of gaussian distributions).
        cluster_covariances (numpy.ndarary): The 3d array of covariances of clusters
                                             (covariance matrices of gaussian distributions).
    """

    pass
