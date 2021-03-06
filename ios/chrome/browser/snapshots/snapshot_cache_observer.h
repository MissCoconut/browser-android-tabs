// Copyright 2017 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef IOS_CHROME_BROWSER_SNAPSHOTS_SNAPSHOT_CACHE_OBSERVER_H_
#define IOS_CHROME_BROWSER_SNAPSHOTS_SNAPSHOT_CACHE_OBSERVER_H_

#import <Foundation/Foundation.h>

@class SnapshotCache;

// Interface for listening to events occurring to the SnapshotCache.
@protocol SnapshotCacheObserver
@optional
// Tells the observing object that the |snapshot_cache| was updated with a new
// snapshot for |tab_id|.
- (void)snapshotCache:(SnapshotCache*)snapshotCache
    didUpdateSnapshotForTab:(NSString*)tabID;
@end

#endif  // IOS_CHROME_BROWSER_SNAPSHOTS_SNAPSHOT_CACHE_OBSERVER_H_
