import homcloud.plotly_3d as p3d


class BitmapOptimal1Cycle:
    """The class represents an optimal (not volume-optimal) 1-cycle for bitmap.

    Computing volume-optimal cycle is very expensive for 3-D and
    higher dimensional cubical filtration. To fight against such
    a huge filtration, :meth:`Pair.optimal_1_cycle` is available.
    This method returns an instance of this class.
    """

    def __init__(self, orig):
        self.orig = orig

    def birth_time(self):
        """
        Returns:
            float: The birth time.
        """
        return self.orig.birth_time

    def death_time(self):
        """
        Returns:
            float: The death time.
        """
        return self.orig.death_time

    def birth_position(self):
        """
        Returns:
            tuple of float*N: The coordinate of birth position. (N: dimension)
        """
        return self.orig.path[0]

    def path(self):
        """
        Returns the path (loop) of the optimal 1-cycle.

        The first item and the last item is the same as :meth:`birth_position`.

        Returns:
            list of coord: The list of vertices of the loop ordered by the path
        """
        return self.orig.path

    def boundary_points(self):
        """
        Returns:
            list of coord: The list of vertices in the loop. Any vertex
                in the list is unique.
        """
        return self.orig.boundary_points()

    def to_plotly3d_trace(self, color=None, name=""):
        """
        Constructs a plotly's trace object to visualize the optimal 1-cycle

        Args:
            color (string or None): The name of the color
            name (string): The name of the object

        Returns:
            plotly.graph_objects.Mesh3d: Plotly's trace object
        """
        return p3d.Voxels(self.path(), color, name)

    to_plotly3d = to_plotly3d_trace

    def to_pyvista_mesh(self):
        """
        Constructs a PyVista's mesh object to visualize the optimal 1-cycle

        Returns:
            pyvista.PolyData: PyVista's mesh object
        """
        import homcloud.pyvistahelper as pvhelper

        return pvhelper.SparseVoxels(self.path())
