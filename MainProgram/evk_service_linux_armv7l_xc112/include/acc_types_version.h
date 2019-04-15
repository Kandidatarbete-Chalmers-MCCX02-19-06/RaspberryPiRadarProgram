// Copyright (c) Acconeer AB, 2017-2018
// All rights reserved

#ifndef ACC_TYPES_VERSION_H_
#define ACC_TYPES_VERSION_H_

#ifdef __cplusplus
extern "C" {
#endif

#define ACC_VERSION_LENGTH_MAX (60)

typedef struct {
	char	commit[ACC_VERSION_LENGTH_MAX];
	char	status[ACC_VERSION_LENGTH_MAX];
	char	tag[ACC_VERSION_LENGTH_MAX];
	char	version[ACC_VERSION_LENGTH_MAX];
} acc_version_t;

#ifdef __cplusplus
}
#endif

#endif
