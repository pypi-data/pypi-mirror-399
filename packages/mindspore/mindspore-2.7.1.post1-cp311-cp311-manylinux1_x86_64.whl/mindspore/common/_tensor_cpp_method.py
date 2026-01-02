# Copyright 2024 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Add tensor cpp methods for stub tensor"""

tensor_cpp_methods = ['expand_as', 'clamp', 'clip', 'view', 'argmax', 'expm1', 'masked_scatter', 'square', 'to', 'ceil', 'allclose', 'scatter_', 'tanh', 'minimum', 'all', 'squeeze', 'cosh', 'floor_divide_', '__ifloordiv__', 'isneginf', 'reciprocal', 'inverse', 'remainder_', '__imod__', 'new_ones', 'xlogy', 'triu', 'narrow', 'subtract', 'atan', 'arctan', 'bincount', 'diag', 'fill_diagonal_', 'true_divide', 'log', 'sqrt', 'logical_not', 'exp_', 'logsumexp', 'bitwise_not', 'cumsum', 'bitwise_and', '__and__', 'prod', 'matmul', 'logical_or', 'add_', '__iadd__', 'mean', 'erf', 'isclose', 'reshape', 'atan2', 'arctan2', 'floor', 'frac', 'eq', 'median', 'sin', 'tril', 'hardshrink', 'flatten', 'div_', '__itruediv__', 'sum', 'split', 'masked_scatter_', 'unbind', 'put_', 'remainder', 'transpose', 'logaddexp2', 'floor_divide', 'scatter', 'acos', 'arccos', 'argmin', 'scatter_add', 'asin', 'arcsin', 'exp', 'maximum', 'neg', 'negative', 'fmod', 'take', 'baddbmm', 'atanh', 'arctanh', 'addbmm', 'logical_xor', 'select', 'new_full', 'where', 'masked_select', 'gather', 'index', 'logical_and', 'mul_', '__imul__', 'repeat_interleave', 'log2', 'chunk', 'mul', 'outer', 'rsqrt', 'index_select', 'imag', 'any', 'sort', 'tile', 'lerp', 'isfinite', 'roll', 'isinf', 'gcd', 'view_as', 'index_fill_', 'sinc', 'histc', 'abs', 'absolute', '__abs__', 'greater', 'gt', 'var', 'greater_equal', 'ge', 'trunc', 'nan_to_num', 'min', 'addmm', 'addmv', 'masked_fill_', 'copy_', 'topk', 'new_zeros', 'tan', 'sub_', '__isub__', 'asinh', 'arcsinh', 'logaddexp', 'type_as', 'sigmoid', 'add', '__add__', 'masked_fill', 'acosh', 'arccosh', 'unsqueeze', 'max', 'less_equal', 'le', '__mod__', 'clone', 'less', 'lt', 'count_nonzero', 'unique', 'nansum', 'argsort', 'kthvalue', 'broadcast_to', 'pow', '__pow__', 'index_copy_', 'fill_', 'sub', '__sub__', 'mm', 'log10', 'sigmoid_', 'dot', 'new_empty', 'cos', 'addcdiv', 'repeat', 'index_add', 'log_', 'round', 'real', 'not_equal', 'ne', 'log1p', 'permute', 'bitwise_or', '__or__', 'bitwise_xor', '__xor__', 'sinh', 'std', 'div', 'divide', 't', 'erfc']
