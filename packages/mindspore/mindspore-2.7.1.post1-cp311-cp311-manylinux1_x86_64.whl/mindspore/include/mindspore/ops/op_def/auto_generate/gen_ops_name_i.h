/**
 * Copyright 2023-2025 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#ifndef MINDSPORE_CORE_OP_NAME_I_H_
#define MINDSPORE_CORE_OP_NAME_I_H_

namespace mindspore::ops {
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameInplaceMatmulAdd = "InplaceMatmulAdd";
constexpr auto kNameInplaceSigmoid = "InplaceSigmoid";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameInplaceRemainderTensorScalar = "InplaceRemainderTensorScalar";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameImagView = "ImagView";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInplaceRemainderTensorTensor = "InplaceRemainderTensorTensor";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameInplaceIndexCopy = "InplaceIndexCopy";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameInplaceBernoulliTensor = "InplaceBernoulliTensor";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameInnerMoeTokenUnpermute = "InnerMoeTokenUnpermute";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameInplaceMaskedScatter = "InplaceMaskedScatter";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameInnerUnique = "InnerUnique";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameInplaceIndexFillTensor = "InplaceIndexFillTensor";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInplaceSign = "InplaceSign";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInplaceBernoulliScalar = "InplaceBernoulliScalar";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameInplaceIndexFillScalar = "InplaceIndexFillScalar";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameInplaceSiLU = "InplaceSiLU";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameInplaceExponential = "InplaceExponential";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_
