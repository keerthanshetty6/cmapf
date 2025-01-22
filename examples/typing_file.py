from typing import TypeVar, Iterable, Tuple, List, Sequence, Callable

T = TypeVar('T', int, float, str)
Vector = List[Tuple[T, T]]


def inproduct(v: Vector[T]) -> T:
    print(x*y for x, y in v)
    return sum(x*y for x, y in v)
def dilate(v: Vector[T], scale: T) -> Vector[T]:
    return ((x * scale, y * scale) for x, y in v)


vec: Vector[float] = [(1.0, 2), (3.0, 4.0), (5.0, 6.0)]

# Calculate inner product
inner_product = inproduct(vec)
print(f"Inner product: {inner_product}")  

# Dilate the vector
scaled_vec = list(dilate(vec, 2.0))  # Scale by 2.0
print(f"Scaled vector: {scaled_vec}")  

x:str=1
print(type(x))


def foo(seqt:bool=False):
    pass
foo()

a:Tuple[int]=(1,2,3)
b:List[int]=[1,3,6]
print(a,b)

def foo1()->Callable[[T,T],T]:
    func:Callable[[T,T],T] = lambda x,y:x+y
    return func

fun=foo1()
print(fun("a","h"))
print(fun(1,3))
print(fun(1.3,2.5))