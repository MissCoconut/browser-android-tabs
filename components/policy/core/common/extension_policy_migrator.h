// Copyright 2018 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef COMPONENTS_POLICY_CORE_COMMON_EXTENSION_POLICY_MIGRATOR_H_
#define COMPONENTS_POLICY_CORE_COMMON_EXTENSION_POLICY_MIGRATOR_H_

#include "base/containers/span.h"
#include "components/policy/core/common/policy_bundle.h"
#include "components/policy/policy_export.h"

namespace policy {

// A helper class that migrates a deprecated policy to a new policy across
// domain boundaries, by setting up the new policy based on the old one. It can
// migrate a deprecated extension policy to a new Chrome policy.
//
// For migrations that are only in the Chrome domain: you should use
// |LegacyPoliciesDeprecatingPolicyHandler| instead.
class POLICY_EXPORT ExtensionPolicyMigrator {
 public:
  virtual ~ExtensionPolicyMigrator();

  // If there are deprecated policies in |bundle|, set the value of the new
  // policies accordingly.
  virtual void Migrate(PolicyBundle* bundle) = 0;

  // Indicates how to rename a policy when migrating from the extension domain
  // to the Chrome domain.
  struct Migration {
    // Old name for the policy, in the extension domain.
    const char* old_name;
    // New name for the policy, in the Chrome domain.
    const char* new_name;
  };

 protected:
  // Helper function intended for implementers who want to rename policies and
  // copy them from an extension domain to the Chrome domain. If one of the
  // Chrome domain policies is already set, it is not overridden.
  void CopyPoliciesIfUnset(PolicyBundle* bundle,
                           const std::string& extension_id,
                           base::span<const Migration> migrations);
};

}  // namespace policy

#endif  // COMPONENTS_POLICY_CORE_COMMON_EXTENSION_POLICY_MIGRATOR_H_
