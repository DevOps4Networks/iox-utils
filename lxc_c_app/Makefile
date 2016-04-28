#
# @file
#	Makefile
#
# @description
#	Makefile used to create a simple IOx native C++ application
#
# @copyright
#	Copyright (c) 2015-2016 by Cisco Systems, Inc.
#	All rights reserved.
#

# Include common definitions and utilities makefile fragment
include prologue.mk


# Select the target machine to build this application for
#YOCTO_MACHINE ?= ie4k-lxc
YOCTO_MACHINE ?= ir800-lxc
#YOCTO_MACHINE ?= isr800-lxc
#YOCTO_MACHINE ?= isr800-qemu
YOCTO_VERSION = 1.7

# Base image - this application needs python interpreter
YOCTO_IMAGE_TARGET = iox-core-image-cpp

# This application performs rootfs image post processing; we need .tar.gz from Yocto
ROOTFS_IMAGE_POSTPROCESSING = 1

# Include common definitions and utilities for native apps
# Note: Must have defined the following variables before including this one
# - YOCTO_MACHINE
# - YOCTO_VERSION
# - YOCTO_IMAGE_TARGET
# - ROOTFS_IMAGE_POSTPROCESSING
include native.mk

# Yocto mirror location (optional)
YOCTO_MIRROR ?=

# C++ application binary
PROGRAM_BIN = $(THE_APP)

#
# Default Makefile Target
#
all: setup $(APP_PKG) teardown

#
# Application specific setup of project
# This setup ensures that the right local.conf is configured for the project
#
.PHONY = setup
setup: setup_common

#
# Create the application package
#
$(APP_PKG): $(APP_PKG_DESCRIPTOR) $(OUTPUT_ROOTFS_IMAGE) $(OUTPUT_KERNEL_IMAGE)
	$(call separator)
	@echo "Creating the application package..."
	@cd $(OUTPUT_DIR) && \
		$(IOX) package create --proj-file $(PROJECT_CONFIG) --img-id $(YOCTO_MACHINE)
	mv $(OUTPUT_DIR)/application.tar $@
	@echo "Done"

# Command set to use to generate a new LXC rootfs
ROOTFS_REPACK_SCRIPT = \
	$(IMG_BLDR) -c extract -d $(ROOTFS_STAGING_DIR) -i $(abspath $<) && \
    cp $(PROGRAM_BIN) $(ROOTFS_STAGING_DIR)/usr/bin && \
	$(IMG_BLDR) -c pack -p $(YOCTO_PROJECT_DIR) -d $(ROOTFS_STAGING_DIR) -r 0.5 -a 1 -i $@

#
# Ready the final rootfs image using the one built by Yocto build system
#
$(OUTPUT_ROOTFS_IMAGE): $(YOCTO_ROOTFS_IMAGE) $(PROGRAM_BIN)
	$(call separator)
	$(call mk_dir,$(@D))
	$(RM) -rf $(ROOTFS_STAGING_DIR)
	$(RM) -rf $@
	$(call mk_dir,$(ROOTFS_STAGING_DIR))
	@echo -e "$(ROOTFS_REPACK_SCRIPT)" | $(FAKEROOT);
	@echo "Done"

#
# Copy the kernel to the staging directory.
# This application doesn't modify the kernel, copy as is
#
$(OUTPUT_KERNEL_IMAGE): $(YOCTO_KERNEL_IMAGE)
	$(call separator)
	$(call mk_dir,$(@D))
	cp $< $@
	touch $@
	@echo "Done"

#
# Build the Yocto rootfs image
# If the Yocto project configuration file is modified, we want to rebuild the image
#
$(YOCTO_ROOTFS_IMAGE): $(YOCTO_PROJECT_LOCAL_CONF)
	$(call separator)
	@echo "Building image: $(YOCTO_IMAGE_TARGET)..."
	@cd $(YOCTO_PROJECT_DIR) && \
		source ./SOURCEME && \
		bitbake $(YOCTO_IMAGE_TARGET) -c clean && \
		bitbake $(YOCTO_IMAGE_TARGET)
	@echo "Done"

#
# Create the build environment setup file
#
$(BUILD_ENV_FILE): $(YOCTO_PROJECT_LOCAL_CONF)
	$(call separator)
	$(IOX) ldsp execute yocto-1.7 buildenv create -p $(YOCTO_PROJECT_DIR)

#
# Source the build environment script and re-invoke this makefile for PROGRAM_BIN target
# The re-invocation step is required only for compiling the C++ program with the target
# build environment
# Once the re-invocation is done, it will go back to the original pristine environment
# for executing the rest of the steps
#

#
# Application specific cleanup tasks after each run
#
.PHONY = teardown
teardown:

#
# Remove some of the output files created by the build process
#
clean:
	$(call separator)
	@echo "Cleaning up application generated files..."
	$(RM) -rf $(APP_PKG) $(OUTPUT_YOCTO_MACHINE_DIR)
	@echo "Done"

#
# Remove all output files created by the build process
#
cleanall: clean
	$(call separator)
	@echo "Cleaning up all build generated files..."
	$(RM) -rf $(OUTPUT_DIR)
	@echo "Done"

#
# Simple debug target to debug this Makefile
#
debug:
	$(call separator)
	$(call debug_common)
	$(call debug_native)

.PHONY: cleanall clean debug
