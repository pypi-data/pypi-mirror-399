def cacfar1d(x, ntrain=3, nguard=1, pfa=1e-4, mode='sql', alpha='auto', pmod='reflect', pval=0):
    """cacfar1d

    see https://www.mathworks.com/help/phased/ug/constant-false-alarm-rate-cfar-detection.html

    Parameters
    ----------
    x : tensor
        input, N x L or L
    ntrain : int, optional
        the number of training cells, by default 3
    nguard : int, optional
        the number of guarding cells, by default 1
    pfa : float, optional
        probility of flase alarm, by default 1e-4
    mode : str, optional
        ``'sql'`` for squere law, by default 'sql'
    alpha : str or float, optional
        threshold factor, ``'auto'`` or any float value
    pmod : str, optional
        padding mode, ``'constant'``, ``'reflect'``, ``'replicate'`` or ``'circular'``. Default: ``'constant'``
    pval : float, optional
        padding value for constant mode, by default 0

    Examples
    --------

    ::

        x = th.zeros(100)
        x[50] = 1
        x[80] = 0.5
        cfarth = cacfar1d(x)

        print(th.where(x > cfarth))

    """

def cacfar2d(x, ntrain=(3, 3), nguard=(1, 1), pfa=1e-4, mode='sql', alpha='auto', pmod='reflect', pval=0):
    """cacfar2d

    Parameters
    ----------
    x : tensor
        input, N x H x W or H x W
    ntrain : list or tuple, optional
        the number of training cells, by default (3, 3, 3)
    nguard : list or tuple, optional
        the number of guarding cells, by default (1, 1)
    pfa : float, optional
        probility of flase alarm, by default 1e-4
    mode : str, optional
        ``'sql'`` for squere law, by default 'sql'
    alpha : str or float, optional
        threshold factor, ``'auto'`` or any float value
    pmod : str, optional
        padding mode, ``'constant'``, ``'reflect'``, ``'replicate'`` or ``'circular'``. Default: ``'constant'``
    pval : float, optional
        padding value for constant mode, by default 0

    Examples
    --------

    ::

        x = th.zeros(100, 100)
        x[50, 60] = 1
        x[80, 90] = 0.5
        cfarth = cacfar2d(x)

        print(th.where(x > cfarth), "cacfar2d")

    """

def cacfar3d(x, ntrain=(3, 3, 3), nguard=(1, 1, 1), pfa=1e-4, mode='sql', alpha='auto', pmod='reflect', pval=0):
    """cacfar3d

    Parameters
    ----------
    x : tensor
        input, N x L or L
    ntrain : list or tuple, optional
        the number of training cells, by default (3, 3, 3)
    nguard : list or tuple, optional
        the number of guarding cells, by default (1, 1, 1)
    pfa : float, optional
        probility of flase alarm, by default 1e-4
    mode : str, optional
        ``'sql'`` for squere law, by default 'sql'
    alpha : str or float, optional
        threshold factor, ``'auto'`` or any float value
    pmod : str, optional
        padding mode, ``'constant'``, ``'reflect'``, ``'replicate'`` or ``'circular'``. Default: ``'constant'``
    pval : float, optional
        padding value for constant mode, by default 0

    Examples
    --------

    ::

        x = th.zeros(100, 100, 100)
        x[50, 60, 30] = 1
        x[80, 90, 70] = 0.5
        cfarth = cacfar3d(x)

        print(th.where(x > cfarth), "cacfar3d")

    """


