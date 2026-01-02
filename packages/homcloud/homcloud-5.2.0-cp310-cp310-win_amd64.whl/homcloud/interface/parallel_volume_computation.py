from concurrent.futures import ProcessPoolExecutor


def _parallel_task(task_params):
    methodname, nth, volume_params = task_params

    pair = shared_pd.pair(nth)
    volume_params["return_failure_if_not_found"] = True
    return getattr(pair, methodname)(**volume_params).dump_to_dict()


def _worker_init(path, degree):
    import homcloud.interface as hc

    global shared_pd
    shared_pd = hc.PDList(path).dth_diagram(degree)


def parallel_volume_computation(optimal_or_stable, pd, pairs_and_params, max_workers=None):
    """
    Compute optimal / stable volume parallely.

    Summary of benchmark result: 3x faster with max_workers=8 for 200 birth-death pairs.

    Args:
        optimal_or_stable (str): "optimal_volume" or "stable_volume"
        pd (:class:`PD`): The diagram used in the volume computation
        pairs_and_params (list[tuple[:class:`Pair`, dict]]): The list of tuples of
            (pair, volume computation parameter). The computation parameter should be given
            by dict whose keys are parameter names.
        max_workers (Option[int]): The maximum number of concurrent computation workers.
            This parameter is passed to concurrent.futures.ProcessPoolExecutor.
            See the python's official documentation of concurrent.futures.

    Returns:
        list[VolumeFailure | OptimalVolume | StableVolume]: The list of volumes.
        VolumeFailure object is used to represent the failure of a computation.

    Remarks:
        The `save_to` option is required when persistence diagrams are computed if you want
        to use this functionality.
        If not, this function raises an ValueError exception.
        This function is not thread safe. Do not call this function parallely.
        Do not call this function under multi-thread environment.

    Example:
        >>> import homcloud.interface as hc
        >>>
        >>> hc.PDList(hc.example_data("tetrahedron"), save_boundary_map=True, save_to="tetrahedron.pdgm")
        >>> pd1 = hc.PDList("tetrahedron.pdgm").dth_diagram(1)
        >>> # Computes all stable volumes of pd1's pairs parallely with eight workers.
        >>> results = hc.parallel_volume_computation(
        >>>     "stable_volume", pd1,  [(pair, {"threshold": 0.01}) for pair in pd1.pairs()], 8
        >>> )
        `results` has all stable volumes.

    """
    from homcloud.interface.optimal_volume import Volume

    assert optimal_or_stable in ["optimal_volume", "stable_volume"]

    if pd.path is None:
        raise ValueError("save_to must be given for parallel computation when PDs are computed")

    with ProcessPoolExecutor(
        max_workers=max_workers,
        initializer=_worker_init,
        initargs=(pd.path, pd.degree),
    ) as executor:
        results = executor.map(
            _parallel_task,
            [(optimal_or_stable, pair.nth, param) for (pair, param) in pairs_and_params],
        )
        return [Volume.restore_from_dict(pd, result) for result in results]
